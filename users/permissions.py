from rest_framework import permissions

from notes.models import ContentPayment


class IsOwner(permissions.BasePermission):
    """Класс определяет права для группы пользователей владельцев/создателей объекта"""

    message = "Not allowed to retrieve, update or destroy not owner's habits"

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True


class SubscribedUser(permissions.BasePermission):
    """Класс определяет права для групп пользователей оплативших подписку"""

    message = "Allowed to publish paid content"

    def has_permission(self, request, view):
        if request.user.subscription_active:
            return True


class IsModer(permissions.BasePermission):
    """Класс определяет права для групп пользователей назначенных модераторами платформы"""

    message = "Moder is allowed to create, retrieve, update and destroy content"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class Buyer(permissions.BasePermission):
    """Класс определяет права для групп пользователей оплативших контент"""

    message = "Buyer is allowed to only retrieve only bought content"

    def has_object_permission(self, request, view, obj):
        if obj in ContentPayment.objects.filter(user=request.user).get(
            "paid_content"
        ):
            return True
