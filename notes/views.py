import stripe
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework import status
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, TemplateView

from users.models import Payment
from users.services import create_stripe_price, create_stripe_session
from .forms import FreeContentForm, PaidContentForm

from .models import PaidContent, FreeContent, BuyerSubscription, ContentPayment

from users.permissions import IsOwner, IsModer, Buyer

from rest_framework.permissions import AllowAny, IsAuthenticated


def contacts(request):
    return render(request, "notes/contacts.html")


class BuyerSubscriptionMixin:
    """Mixin для проверки активной подписки на контент у пользователя."""

    def dispatch(self, request, *args, **kwargs):
        content_id = request.get("paid_content_id")
        content = PaidContent.objects.filter(id=content_id)
        user = request.user
        subscription = PaidContent.objects.filter(content=content, user=user).exists()
        if not subscription:
            return HttpResponseForbidden(
                "Вы не подписаны на этот контент. Требуется покупка подписки."
            )
        return super().dispatch(request, *args, **kwargs)


class UserSubscribedMixin:
    """Mixin для проверки активной подписки на сервис у пользователя."""

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.subscription:
            return HttpResponseForbidden(
                "Для публикации платного контента требуется покупка подписки на сервис."
            )
        return super().dispatch(request, *args, **kwargs)


class MyContentListView(TemplateView):
    """Контроллер просмотра списка контента созданного пользователем"""

    template_name = "notes/my_content_list.html"
    context_object_name = "content"
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            "free_content": FreeContent.objects.filter(user=request.user.id),
            "paid_content": PaidContent.objects.filter(user=request.user.id),
        }
        return self.render_to_response(self.extra_context)


class PaidContentCreateView(CreateView, UserSubscribedMixin):
    """Контроллер создания объекта модели платного контента"""

    model = PaidContent
    form_class = PaidContentForm
    template_name = "notes/paid_content_create.html"
    success_url = reverse_lazy("notes:paid_content_list")
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
    context_object_name = "paid_content"
    template_name = "notes/paid_content_detail.html"
    permission_classes = [
        IsOwner,
        Buyer,
        IsModer,
    ]


class PaidContentUpdateView(UpdateView):
    """Контроллер обновления объекта модели платного контента"""

    model = PaidContent
    form_class = PaidContentForm
    template_name = "notes/paid_content_create.html"
    success_url = reverse_lazy("notes:paid_content_detail")
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
    context_object_name = "paid_content"
    template_name = "notes/paid_content_destroy.html"
    success_url = reverse_lazy("notes:paid_content_list")


class PaidContentListView(ListView):
    """Контроллер просмотра списка объектов модели платного контента"""

    model = PaidContent
    template_name = "notes/paid_content_list.html"
    context_object_name = "paid_content"
    permission_classes = [
        IsAuthenticated,
    ]


class FreeContentCreateView(CreateView):
    """Контроллер создания объекта модели бесплатного контента"""

    model = FreeContent
    form_class = FreeContentForm
    template_name = "notes/free_content_create.html"
    success_url = reverse_lazy("notes:free_content_list")
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
    context_object_name = "free_content"
    template_name = "notes/free_content_detail.html"
    permission_classes = [
        AllowAny,
    ]


class FreeContentUpdateView(UpdateView):
    """Контроллер обновления объекта модели бесплатного контента"""

    model = FreeContent
    form_class = FreeContentForm
    template_name = "notes/free_content_create.html"
    success_url = reverse_lazy("notes:free_content_list")
    permission_classes = [
        IsOwner,
        IsModer,
    ]

    def form_valid(self, form):
        free_content = form.save
        free_content.save()
        return super().form_valid(form)


class FreeContentDeleteView(DeleteView):
    """Контроллер удаления объекта модели бесплатного контента"""

    model = FreeContent
    permission_classes = [
        IsOwner,
        IsModer,
    ]
    context_object_name = "free_content"
    template_name = "notes/free_content_destroy.html"
    success_url = reverse_lazy("notes:free_content_list")


class FreeContentListView(ListView):
    """Контроллер просмотра списка объектов модели бесплатного контента"""

    model = FreeContent
    template_name = "notes/free_content_list.html"
    context_object_name = "free_content"
    permission_classes = [
        AllowAny,
    ]


def create_payment(request, price):
    payment_amount = create_stripe_price(price * 100)
    payment_session = create_stripe_session(payment_amount)
    session_id = payment_session.get("id")
    payment_link = payment_session.get("url")
    payment = Payment.objects.create(
        user=request.user,
        payment_amount=payment_amount["unit_amount"],
        payment_link=payment_link,
        session_id=session_id,
    )
    payment.save()
    return payment


@login_required
def buy_content_subscription(request):
    content_id = request.get("content_id")
    content_price = PaidContent.objects.get(id=content_id).price
    payment = Payment.objects.get(user=request.user)
    if request.method == "POST":
        if not payment:
            payment = create_payment(request, content_price)
            context = {"payment": payment}
            return render(request, "users/buy_paid_content.html", context)
        else:
            try:
                response = stripe.PaymentIntent.retrieve(payment.session_id)
                if response["status"] == "succeeded":
                    request.user.subscription = True
                    payment.status = "paid"
                    return render(request, "notes/paid_content_detail.html")
                else:
                    context = {"payment": payment}
                    return render(request, "users/buy_paid_content.html", context)
            except Exception as ex:
                context = {"payment": payment}
                print(ex)
                return render(request, "users/buy_paid_content.html", context)
    else:
        if not payment:
            payment = create_payment(request, content_price)
            context = {"payment": payment}
            return render(request, "users/buy_paid_content.html", context)
        else:
            try:
                response = stripe.PaymentIntent.retrieve(payment.session_id)
                if response["status"] == "succeeded":
                    request.user.subscription = True
                    payment.status = "paid"
                    return render(request, "notes/buy_paid_content.html")
                else:
                    context = {"payment": payment}
                    return render(request, "users/buy_paid_content.html", context)
            except Exception as ex:
                context = {"payment": payment}
                print(ex)
                return render(request, "users/buy_paid_content.html", context)


class BuyerSubscriptionCreateView(CreateView):
    """Контроллер создания объекта подписки на оплаченный контент"""

    model = BuyerSubscription
    permission_classes = [
        IsAuthenticated,
    ]
    template_name = "notes/buy_content.html"
    success_url = "notes:paid_content_detail"

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
