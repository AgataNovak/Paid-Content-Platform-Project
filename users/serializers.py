from rest_framework import serializers

from .models import Payment, ServiceSubscription
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели User"""

    class Meta:
        model = CustomUser
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели Payment"""

    class Meta:
        model = Payment
        fields = "__all__"


class ServiceSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели ServiceSerializer"""

    class Meta:
        model = ServiceSubscription
        fields = "__all__"
