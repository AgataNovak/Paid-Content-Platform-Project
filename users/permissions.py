from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Класс определяет права для группы пользователей владельцев/создателей объекта"""

    message = "Not allowed to retrieve, update or destroy not owner's habits"

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True


class IsModer(permissions.BasePermission):
    """Класс определяет права для групп пользователей назначенных модераторами платформы"""

    message = "Moder is allowed to create, retrieve, update and destroy content"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()
