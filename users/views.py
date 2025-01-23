import os

from rest_framework import viewsets
from rest_framework import views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, ServiceSubscription, Payment
from .permissions import SubscribedUser
from .serializers import UserSerializer, PaymentSerializer
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)

from .services import create_stripe_price, create_stripe_session


class UserCreateApiView(CreateAPIView):
    """Контроллер создания объекта класса User"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserListApiView(ListAPIView):
    """Контроллер просмотра списка объектов класса User"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserRetrieveApiView(RetrieveAPIView):
    """Контроллер просмотра объекта класса User"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserUpdateApiView(UpdateAPIView):
    """Контроллер обновления объекта класса User"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserDestroyApiView(DestroyAPIView):
    """Контроллер удаления объекта класса User"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserProfileViewSet(viewsets.ModelViewSet):
    """Контроллер операций с личным профилем авторизованного пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()


class ServiceSubscriptionPaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        price = create_stripe_price(os.environ["SERVICE_SUBSCRIPTION_PRICE"])
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.payment_link = payment_link
        payment.save()


class ServiceSubscriptionView(views.APIView):
    """Контроллер создания объекта подписки на услуги сервиса"""

    permission_classes = [IsAuthenticated, ~SubscribedUser]

    def post(self, request):
        payment = Payment.objects.create(user=request.user, content=request.get('content'))
        if payment.session_id.get('payment_status') == 'paid':
            subscription = ServiceSubscription.objects.create(user=request.user)
            subscription.save()
            user = User.objects.filter(id=request.user.id)
            user.subscription = True
            user.save()
            message = f'Пользователь {user.username} подписан на услуги сервиса'
            return Response({"message": message}, status=status.HTTP_200_OK)
        elif payment.session_id.get('payment_status') != 'paid':
            message = f"Подписка ожидает оплаты. Оплатить подписку можно по ссылке - {payment.payment_link}"
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = f"Error. No session id"
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
