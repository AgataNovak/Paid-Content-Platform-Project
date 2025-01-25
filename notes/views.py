import os

from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)
from django.views.generic.edit import (
    CreateView,
    UpdateView, DeleteView
)
from django.views.generic import (
    ListView,
    DetailView, TemplateView
)

from users.models import CustomUser
from users.services import create_stripe_price, create_stripe_session
from .forms import FreeContentForm, PaidContentForm
from .serializers import (
    PaidContentSerializer,
    FreeContentSerializer,
    PaidContentListSerializer,
    PaymentSerializer,
    BuyerSubscriptionSerializer,
)

from .models import PaidContent, FreeContent, BuyerSubscription, ContentPayment

from users.permissions import IsOwner, SubscribedUser, IsModer, Buyer

from rest_framework.permissions import AllowAny, IsAuthenticated


def contacts(request):
    return render(request, 'notes/contacts.html')


class BuyerSubscriptionMixin:
    """Mixin для проверки активной подписки на контент у пользователя."""

    def dispatch(self, request, *args, **kwargs):
        content_id = request.get('paid_content_id')
        content = PaidContent.objects.filter(id=content_id)
        user = request.user
        subscription = PaidContent.objects.filter(content=content, user=user).exists()
        if not subscription:
            return HttpResponseForbidden("Вы не подписаны на этот контент. Требуется покупка подписки.")
        return super().dispatch(request, *args, **kwargs)


class MyContentListView(TemplateView):
    """Контроллер просмотра списка контента созданного пользователем"""

    template_name = 'notes/my_content_list.html'
    context_object_name = 'content'
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            "free_content": FreeContent.objects.filter(user=request.user.id),
            "paid_content": PaidContent.objects.filter(user=request.user.id),
        }
        return self.render_to_response(self.extra_context)


class PaidContentCreateView(CreateView):
    """Контроллер создания объекта модели платного контента"""

    model = PaidContent
    form_class = PaidContentForm
    template_name = 'notes/paid_content_create.html'
    success_url = reverse_lazy('notes:paid_content_list')
    permission_classes = [
        IsAuthenticated,
    ]

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super().form_valid(form)


class PaidContentDetailView(BuyerSubscriptionMixin, DetailView):
    """Контроллер просмотра объекта модели платного контента"""

    model = PaidContent
    context_object_name = 'paid_content'
    template_name = 'notes/paid_content_detail.html'
    permission_classes = [
        IsOwner,
        Buyer,
        IsModer,
    ]


class PaidContentUpdateView(UpdateView):
    """Контроллер обновления объекта модели платного контента"""

    model = PaidContent
    form_class = PaidContentForm
    template_name = 'notes/paid_content_create.html'
    success_url = reverse_lazy('notes:paid_content_detail')
    permission_classes = [
        IsOwner,
        IsModer,
    ]


class PaidContentDeleteView(DetailView):
    """Контроллер удаления объекта модели платного контента"""

    model = PaidContent
    permission_classes = [
        IsOwner,
        IsModer,
    ]
    context_object_name = 'paid_content'
    template_name = 'notes/paid_content_destroy.html'
    success_url = reverse_lazy('notes:paid_content_list')


class PaidContentListView(ListView):
    """Контроллер просмотра списка объектов модели платного контента"""

    model = PaidContent
    template_name = 'notes/paid_content_list.html'
    context_object_name = 'paid_content'
    permission_classes = [
        IsAuthenticated,
    ]


class FreeContentCreateView(CreateView):
    """Контроллер создания объекта модели бесплатного контента"""

    model = FreeContent
    form_class = FreeContentForm
    template_name = 'notes/free_content_create.html'
    success_url = reverse_lazy('notes:free_content_list')
    permission_classes = [
        AllowAny,
    ]

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super().form_valid(form)


class FreeContentDetailView(DetailView):
    """Контроллер просмотра объекта модели бесплатного контента"""

    model = FreeContent
    context_object_name = 'free_content'
    template_name = 'notes/free_content_detail.html'
    permission_classes = [
        AllowAny,
    ]


class FreeContentUpdateView(UpdateView):
    """Контроллер обновления объекта модели бесплатного контента"""

    model = FreeContent
    form_class = FreeContentForm
    template_name = 'notes/free_content_create.html'
    success_url = reverse_lazy('notes:free_content_list')
    permission_classes = [
        IsOwner,
        IsModer,
    ]

    def form_valid(self, form):
        free_content = form.save
        return super().form_valid(form)


class FreeContentDeleteView(DeleteView):
    """Контроллер удаления объекта модели бесплатного контента"""

    model = FreeContent
    permission_classes = [
        IsOwner,
        IsModer,
    ]
    context_object_name = 'free_content'
    template_name = 'notes/free_content_destroy.html'
    success_url = reverse_lazy('notes:free_content_list')


class FreeContentListView(ListView):
    """Контроллер просмотра списка объектов модели бесплатного контента"""

    model = FreeContent
    template_name = 'notes/free_content_list.html'
    context_object_name = 'free_content'
    permission_classes = [
        AllowAny,
    ]


class ContentPaymentCreateAPIView(CreateView):
    model = ContentPayment
    template_name = 'notes/buy_content.html'

    def perform_create(self, serializer):
        payment = ContentPayment.objects.filter(user=self.request.user).exists()
        if payment:
            message = (
                f"Счет на оплату уже создан и доступен по ссылке {payment.payment_link}"
            )
            return Response({"message": message}, status=status.HTTP_409_CONFLICT)
        else:
            payment = serializer.save(user=self.request.user)
            price = create_stripe_price(os.environ["SERVICE_SUBSCRIPTION_PRICE"])
            session_id, payment_link = create_stripe_session(price)
            payment.session_id = session_id
            payment.payment_link = payment_link
            payment.save()


class BuyerSubscriptionCreateView(CreateView):
    """Контроллер создания объекта подписки на оплаченный контент"""

    model = BuyerSubscription
    permission_classes = [
        IsAuthenticated,
    ]
    template_name = 'notes/buy_content.html'
    success_url = 'notes:paid_content_detail'

    def perform_create(self, serializer):
        if BuyerSubscription.objects.filter(
            user=self.request.user,
            content=self.request.get("content_id"),
            is_active=True,
        ).exists():
            return Response(
                {"message": "Подписка на данный контент уже активна."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = ContentPayment.objects.filter(
            user=self.request.user, paid_content=self.request.get("content_id")
        ).exists()
        if not payment:
            payment = ContentPayment.objects.create(
                user=self.request.user, paid_content=self.request.get("content_id")
            )
            payment.save()
            return Response(
                {
                    "message": f"Счет создан и готов к оплате по ссылке {payment.payment_link}"
                },
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            if payment.status != "paid":
                return Response(
                    {
                        "message": f"Подписка на услуги сервиса ожидает оплаты. "
                        f"Пожалуйста, оплатите счет по ссылке {payment.payment_link}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription = BuyerSubscription.objects.create(
                user=self.request.user,
                content=self.request.get("content_id"),
                is_active=True,
            )
            subscription.save()
            return Response(
                {"message": "Подписка на контент активизирована"},
                status=status.HTTP_201_CREATED,
            )
