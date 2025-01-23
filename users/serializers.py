from rest_framework import serializers

from .models import Payment, ServiceSubscription
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели User"""

    class Meta:
        model = User
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор выполняет сериализацию данных для модели Payment"""

    class Meta:
        model = Payment
        fields = "__all__"
