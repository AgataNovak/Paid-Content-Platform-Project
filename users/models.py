from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        unique=True,
        max_length=50,
        blank=False,
        null=False,
        verbose_name="Имя пользователя",
        help_text="Введите имя пользователя",
    )

    email = models.EmailField(
        verbose_name="Email пользователя", help_text="Введите e-mail пользователя"
    )

    avatar = models.ImageField(
        upload_to="users/avatars",
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "phone_number",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель оплаты"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя",
    )

    payment_amount = models.PositiveIntegerField(
        blank=False,
        null=False,
        help_text="Введите сумму к оплате",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Дата создания счета",
        help_text="Введите дату создания счета",
    )

    status = models.CharField(
        default="unpaid",
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Статус оплаты",
        help_text="Введите статус оплаты",
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
        return f"{self.user} - {self.payment_amount} - {self.created_at}"

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
        ordering = ["created_at"]


class ServiceSubscription(models.Model):
    """Модель подписки на услуги сервиса"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя",
    )

    is_active = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        verbose_name="Статус активности подписки",
        help_text="Введите статус активности подписки",
    )

    payment_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату подписки',
        help_text='Введите ссылку на оплату подписки',
    )

    class Meta:
        verbose_name = "Подписка на сервис"
        verbose_name_plural = "Подписки на сервис"
        ordering = ["user"]
