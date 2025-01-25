import os
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, get_object_or_404
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


class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def perform_create(self, serializer):
        payment = Payment.objects.filter(user=self.request.user).exists()
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


class ServiceSubscriptionCreateAPIView(CreateAPIView):
    """Контроллер создания объекта подписки на услуги сервиса"""

    serializer_class = ServiceSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        if ServiceSubscription.objects.filter(
            user=self.request.user, is_active=True
        ).exists():
            return Response(
                {"message": "Подписка на услуги сервиса уже активна."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = Payment.objects.filter(user=self.request.user).exists()
        if not payment:
            payment = Payment.objects.create(
                user=self.request.user,
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
            subscription = ServiceSubscription.objects.create(
                user=self.request.user, is_active=True
            )
            subscription.save()
            return Response(
                {"message": "Подписка на услуги сервиса активизирована"},
                status=status.HTTP_201_CREATED,
            )


class ServiceSubscriptionListAPIView(ListAPIView):
    """Контроллер просмотра списка объектов класса ServiceSubscription"""

    serializer_class = ServiceSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return ServiceSubscription.objects.filter(user=self.request.user)
