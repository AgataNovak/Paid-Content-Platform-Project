from rest_framework.serializers import ModelSerializer

from .models import (
    PaidContent,
    FreeContent,
    ContentPayment,
    BuyerSubscription,
)


class PaidContentSerializer(ModelSerializer):
    """Сериализатор модели платного контента"""

    class Meta:
        model = PaidContent
        fields = "__all__"


class PaidContentListSerializer(ModelSerializer):
    """Сериализатор просмотра списка объектов платного контента"""

    class Meta:
        model = PaidContent
        fields = ["title", "owner", "price"]


class FreeContentSerializer(ModelSerializer):
    """Сериализатор модели бесплатного контента"""

    class Meta:
        model = FreeContent
        fields = "__all__"


class PaymentSerializer(ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели Payment"""

    class Meta:
        model = ContentPayment
        fields = "__all__"


class BuyerSubscriptionSerializer(ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели BuyerSubscription"""

    class Meta:
        model = BuyerSubscription
        fields = "__all__"
