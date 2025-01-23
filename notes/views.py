from rest_framework.response import Response
from rest_framework import views, status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)

from users.services import create_stripe_price, create_stripe_session
from .serializers import (
    PaidContentSerializer,
    FreeContentSerializer,
    PaidContentListSerializer,
    PaymentSerializer
)

from .models import (
    PaidContent,
    FreeContent,
    BuyerSubscription,
    ContentSubscriptionPayment
)

from users.permissions import (
    IsOwner,
    SubscribedUser,
    IsModer,
    Buyer
)

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)


class PaidContentCreateAPIView(CreateAPIView):
    """Контроллер создания объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [SubscribedUser,]


class PaidContentRetrieveAPIView(RetrieveAPIView):
    """Контроллер просмотра объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, Buyer, IsModer,]


class PaidContentUpdateAPIView(UpdateAPIView):
    """Контроллер обновления объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, IsModer,]


class PaidContentDestroyAPIView(DestroyAPIView):
    """Контроллер удаления объекта модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, IsModer,]


class PaidContentListAPIView(ListAPIView):
    """Контроллер просмотра списка объектов модели платного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentListSerializer
    permission_classes = [AllowAny,]


class FreeContentCreateAPIView(CreateAPIView):
    """Контроллер создания объекта модели бесплатного контента"""

    queryset = FreeContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [AllowAny,]


class FreeContentRetrieveAPIView(RetrieveAPIView):
    """Контроллер просмотра объекта модели бесплатного контента"""

    queryset = FreeContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, IsModer,]


class FreeContentUpdateAPIView(UpdateAPIView):
    """Контроллер обновления объекта модели бесплатного контента"""

    queryset = FreeContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, IsModer,]


class FreeContentDestroyAPIView(DestroyAPIView):
    """Контроллер удаления объекта модели бесплатного контента"""

    queryset = PaidContent.objects.all()
    serializer_class = PaidContentSerializer
    permission_classes = [IsOwner, IsModer,]


class FreeContentListAPIView(ListAPIView):
    """Контроллер просмотра списка объектов модели бесплатного контента"""

    queryset = FreeContent.objects.all()
    serializer_class = FreeContentSerializer
    permission_classes = [AllowAny, ]


class ContentSubscriptionPaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = ContentSubscriptionPayment.objects.all()

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        price = create_stripe_price(payment.payment_amount)
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.payment_link = payment_link
        payment.save()


class BuyerSubscriptionView(views.APIView):
    """Контроллер создания объекта подписки на оплаченный контент"""

    permission_classes = [IsAuthenticated,]

    def post(self, request):
        payment = ContentSubscriptionPayment.objects.create(user=request.user, content=request.get('content'))
        if payment.session_id.get('payment_status') == 'paid':
            subscription = BuyerSubscription.objects.create(user=request.user, content=request.data.get('content_id'))
            subscription.save()
            content_title = PaidContent.objects.filter(id=request.data.get('content_id'))
            message = f'Пользователь {request.user.username} подписан на контент "{content_title}"'
            return Response({"message": message}, status=status.HTTP_200_OK)
        elif payment.session_id.get('payment_status') != 'paid':
            message = f"Подписка ожидает оплаты. Оплатить подписку можно по ссылке - {payment.payment_link}"
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = f"Error. No session id"
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
