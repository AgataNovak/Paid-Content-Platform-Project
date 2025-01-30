import stripe
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, TemplateView
from users.services import create_stripe_price, create_stripe_session
from .forms import FreeContentForm, PaidContentForm
from .models import PaidContent, FreeContent, BuyerSubscription, ContentPayment
from users.permissions import IsOwner, IsModer
from rest_framework.permissions import AllowAny, IsAuthenticated


def contacts(request):
    return render(request, "notes/contacts.html")


class BuyerSubscriptionMixin:
    """Mixin для проверки активной подписки на контент у пользователя."""

    def dispatch(self, request, *args, **kwargs):
        content_id = kwargs.get("pk")
        content = get_object_or_404(PaidContent, id=content_id)
        user = request.user
        subscription = BuyerSubscription.objects.filter(
            content=content, user=user, is_active=True
        ).exists()
        if content.user != user:
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
        IsModer,
    ]


class PaidContentUpdateView(UpdateView):
    """Контроллер обновления объекта модели платного контента"""

    model = PaidContent
    form_class = PaidContentForm
    template_name = "notes/paid_content_create.html"
    permission_classes = [
        IsOwner,
        IsModer,
    ]

    def get_success_url(self):
        return reverse_lazy("notes:paid_content_retrieve", args=[self.object.pk])


class PaidContentDeleteView(DeleteView):
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
        form.save
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


def create_payment(request, price, pk):
    content = get_object_or_404(PaidContent, id=pk)
    payment_amount = create_stripe_price(price * 100)
    payment_session = create_stripe_session(payment_amount)
    session_id = payment_session.get("id")
    payment_link = payment_session.get("url")
    payment = ContentPayment.objects.create(
        user=request.user,
        payment_amount=payment_amount["unit_amount"],
        payment_link=payment_link,
        session_id=session_id,
        paid_content=content,
    )
    payment.save()
    return payment


@login_required
def buy_content_subscription(request, pk):
    content = get_object_or_404(PaidContent, id=pk)
    content_price = content.price
    payment_exists = ContentPayment.objects.filter(
        user=request.user, paid_content=content
    ).exists()

    if payment_exists:
        payment = ContentPayment.objects.get(user=request.user, paid_content=content)

        try:
            response = stripe.PaymentIntent.retrieve(payment.session_id)

            if response["status"] == "succeeded":
                request.user.subscription = True
                request.user.save()
                payment.status = "paid"
                payment.save()
                return render(request, "notes/paid_content_detail.html")
            else:
                context = {"payment": payment}
                return render(request, "notes/buy_paid_content.html", context)
        except Exception as ex:
            context = {"payment": payment}
            print(ex)
            return render(request, "notes/buy_paid_content.html", context)

    payment = create_payment(request, content_price, pk)
    context = {"payment": payment}
    return render(request, "notes/buy_paid_content.html", context)
