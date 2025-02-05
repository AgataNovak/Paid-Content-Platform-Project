import os
import stripe
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from rest_framework.permissions import AllowAny
from .models import Payment
from .services import create_stripe_price, create_stripe_session


stripe.api_key = os.environ["STRIPE_API_KEY"]


class UserCreateView(CreateView):
    """Контроллер создания объекта класса User"""

    permission_classes = (AllowAny,)
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("notes:free_content_list")

    def form_valid(self, form):
        to_return = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        return to_return

    def form_invalid(self, form):
        return super().form_invalid(form)


@login_required
def profile(request):
    return render(request, "users/user_detail.html")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    success_url = reverse_lazy("notes:free_content_list")


class CustomLogoutView(LogoutView):
    template_name = "notes/free_content_list.html"
    success_url = reverse_lazy("notes:free_content_list")


def create_payment(request):
    payment_amount = create_stripe_price(
        int(os.environ["SERVICE_SUBSCRIPTION_PRICE"]) * 100
    )
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
def buy_subscription(request):
    payment_exists = Payment.objects.filter(user=request.user).exists()
    if payment_exists:
        payment = Payment.objects.get(user=request.user)
        try:
            response = stripe.PaymentIntent.retrieve(payment.session_id)
            if response["status"] == "succeeded":
                request.user.subscription = True
                request.user.save()
                payment.status = "paid"
                payment.save()
                return render(request, "notes/paid_content_list.html")
            else:
                return render(
                    request, "users/buy_subscription.html", {"payment": payment}
                )
        except Exception as ex:
            context = {"payment": payment}
            print(ex)
            return render(request, "users/buy_subscription.html", context)
    else:
        payment = create_payment(request)
        context = {"payment": payment}
        return render(request, "users/buy_subscription.html", context)
