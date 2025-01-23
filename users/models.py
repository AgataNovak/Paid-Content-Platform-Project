import os

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="Имя пользователя",
        help_text="Введите имя пользователя"
    )

    email = models.EmailField(
        verbose_name="Email пользователя",
        help_text="Введите e-mail пользователя"
    )

    avatar = models.ImageField(
        upload_to="static/images/users/avatars/",
        verbose_name="Фото профиля пользователя",
        blank=True,
        null=True,
        help_text="Загрузите фото профиля пользователя",
    )

    phone_number = models.CharField(
        unique=True,
        max_length=35,
        verbose_name="Телефон пользователя",
        blank=True,
        null=True,
        help_text="Введите номер телефона пользователя",
    )

    subscription = models.BooleanField(
        default=False,
        verbose_name="Наличие подписки",
        help_text="Укажите наличие подписки",
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = [
        "username",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель оплаты контента"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя"
    )

    payment_amount = models.PositiveIntegerField(
        blank=False,
        null=False,
        help_text="Введите сумму к оплате",
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Дата оплаты",
        help_text="Введите дату оплаты",
    )

    session_id = models.CharField(
        max_length=250,
        verbose_name="id сессии",
        blank=False,
        null=False,
        help_text="Укажите id сессии",
    )

    payment_link = models.URLField(
        max_length=400,
        blank=False,
        null=False,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )

    def __str__(self):
        return f"{self.user} - {self.paid_content} - {self.payment_amount} - {self.payment_date}"

    class Meta:
        verbose_name = "Покупка доступа к записи"
        verbose_name_plural = "Покупки доступа к записям"
        ordering = ["payment_date"]


class ServiceSubscription(models.Model):
    """Модель подписки на услуги сервиса"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя"
    )

    class Meta:
        verbose_name = "Подписка на услуги сервиса"
        verbose_name_plural = "Подписки на услуги сервиса"
        ordering = ["user"]
