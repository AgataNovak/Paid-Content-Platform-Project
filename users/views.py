import os
import requests
import stripe
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib import auth
from .forms import CustomUserCreationForm
from .permissions import IsOwner, IsModer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, ServiceSubscription, Payment
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
    PaymentSerializer,
    ServiceSubscriptionSerializer,
)
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)
from .services import create_stripe_price, create_stripe_session


stripe.api_key = os.environ['STRIPE_API_KEY']


class UserCreateView(CreateView):
    """Контроллер создания объекта класса User"""

    permission_classes = (AllowAny,)
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('notes:free_content_list')

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
    return render(request, 'users/user_detail.html')


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    success_url = reverse_lazy('notes:free_content_list')


class CustomLogoutView(LogoutView):
    template_name = 'notes/free_content_list.html'
    success_url = reverse_lazy('notes:free_content_list')


class UserProfileViewSet(viewsets.ModelViewSet):
    """Контроллер операций с личным профилем авторизованного пользователя"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()


def create_payment(request):
    payment_amount = create_stripe_price(int(os.environ["SERVICE_SUBSCRIPTION_PRICE"]) * 100)
    payment_session = create_stripe_session(payment_amount)
    session_id = payment_session.get('id')
    payment_link = payment_session.get('url')
    payment = Payment.objects.create(
        user=request.user,
        payment_amount=payment_amount["unit_amount"],
        payment_link=payment_link,
        session_id=session_id
    )
    payment.save()
    return payment


@login_required
def buy_subscription(request):
    payment = Payment.objects.get(user=request.user)
    if request.method == 'POST':
        if not payment:
            payment = create_payment(request)
            context = {'payment': payment}
            return render(request, 'users/buy_subscription.html', context)
        else:
            try:
                response = stripe.PaymentIntent.retrieve(payment.session_id)
                if response["status"] == "succeeded":
                    request.user.subscription = True
                    payment.status = 'paid'
                    return render(request, 'notes/paid_content_list.html')
                else:
                    context = {'payment': payment}
                    return render(request, 'users/buy_subscription.html', context)
            except Exception as ex:
                context = {'payment': payment}
                print(ex)
                return render(request, 'users/buy_subscription.html', context)
    else:
        if not payment:
            payment = create_payment(request)
            context = {'payment': payment}
            return render(request, 'users/buy_subscription.html', context)
        else:
            try:
                response = stripe.PaymentIntent.retrieve(payment.session_id)
                if response["status"] == "succeeded":
                    request.user.subscription = True
                    payment.status = 'paid'
                    return render(request, 'notes/paid_content_list.html')
                else:
                    context = {'payment': payment}
                    return render(request, 'users/buy_subscription.html', context)
            except Exception as ex:
                context = {'payment': payment}
                print(ex)
                return render(request, 'users/buy_subscription.html', context)
