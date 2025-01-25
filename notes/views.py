import os

from django.shortcuts import render
from django.urls import reverse_lazy
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
    UpdateView
)
from django.views.generic import (
    ListView,
    DetailView
)
from users.services import create_stripe_price, create_stripe_session
from .forms import FreeContentForm
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


class PaidContentCreateAPIView(CreateAPIView):
    """Контроллер создания объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [
        SubscribedUser,
    ]


class PaidContentRetrieveAPIView(RetrieveAPIView):
    """Контроллер просмотра объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [
        IsOwner,
        Buyer,
        IsModer,
    ]


class PaidContentUpdateAPIView(UpdateAPIView):
    """Контроллер обновления объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [
        IsOwner,
        IsModer,
    ]


class PaidContentDestroyAPIView(DestroyAPIView):
    """Контроллер удаления объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [
        IsOwner,
        IsModer,
    ]


class PaidContentListAPIView(ListAPIView):
    """Контроллер просмотра списка объектов модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentListSerializer
    permission_classes = [
        AllowAny,
    ]


# class FreeContentCreateAPIView(CreateAPIView):
#     """Контроллер создания объекта модели бесплатного контента"""
#
#     queryset = FreeContent.objects.all()
#     serializer_class = FreeContentSerializer
#     permission_classes = [AllowAny,]
#     template_name = 'notes/free_content_create.html'
#     success_url = reverse_lazy('notes:free_content_list')


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



# class FreeContentRetrieveAPIView(RetrieveAPIView):
#     """Контроллер просмотра объекта модели бесплатного контента"""
#
#     queryset = FreeContent.objects.all()
#     serializer_class = FreeContentSerializer
#     permission_classes = [AllowAny,]
#     context_object_name = 'free_content'
#     template_name = 'notes/free_content_detail.html'


class FreeContentDetailView(DetailView):
    """Контроллер просмотра объекта модели бесплатного контента"""

    model = FreeContent
    context_object_name = 'free_content'
    template_name = 'notes/free_content_detail.html'
    permission_classes = [
        AllowAny,
    ]

# class FreeContentUpdateAPIView(UpdateAPIView):
#     """Контроллер обновления объекта модели бесплатного контента"""
#
#     queryset = FreeContent.objects.all()
#     serializer_class = PaidContentSerializer
#     permission_classes = [
#         IsOwner,
#         IsModer,
#     ]
#     template_name = 'notes/free_content_create.html'
#     success_url = reverse_lazy('notes:free_content_list')


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
        # user = self.request.user
        # free_content.user = user
        # free_content.save()
        return super().form_valid(form)


class FreeContentDestroyAPIView(DestroyAPIView):
    """Контроллер удаления объекта модели бесплатного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [
        IsOwner,
        IsModer,
    ]
    template_name = 'notes/free_content_destroy.html'
    success_url = reverse_lazy('notes:free_content_list')


# class FreeContentListAPIView(ListAPIView):
#     """Контроллер просмотра списка объектов модели бесплатного контента"""
#
#     queryset = FreeContent.objects.all()
#     serializer_class = FreeContentSerializer
#     permission_classes = [
#         AllowAny,
#     ]
#
#     def get(self, request, *args, **kwargs):
#         free_content = FreeContent.objects.all()
#         context = {'free_content': free_content}
#         return render(request, 'notes/free_content_list.html', context=context)

class FreeContentListView(ListView):
    """Контроллер просмотра списка объектов модели бесплатного контента"""

    model = FreeContent
    template_name = 'notes/free_content_list.html'
    context_object_name = 'free_content'
    permission_classes = [
        AllowAny,
    ]


class ContentPaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = ContentPayment.objects.all()

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


class BuyerSubscriptionCreateAPIView(CreateAPIView):
    """Контроллер создания объекта подписки на оплаченный контент"""

    serializer_class = BuyerSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

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
