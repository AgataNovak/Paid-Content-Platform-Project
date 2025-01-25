from django.db import models
from users.models import CustomUser


class PaidContent(models.Model):
    """Модель платной записи"""

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )

    title = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Название записи",
        help_text="Введите название записи",
    )

    note_body = models.CharField(
        max_length=2000,
        default="Запись отсутствует",
        null=True,
        blank=True,
        verbose_name="Запись",
        help_text="Введите запись",
    )

    video_link = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Ссылка на видео-материал",
        help_text="Введите ссылку на видео-материал",
    )

    price = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
        verbose_name="Цена доступа к записи",
        help_text="Введите цену доступа к записи в рублях",
    )


class FreeContent(models.Model):
    """Модель бесплатной записи"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )

    title = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Название записи",
        help_text="Введите название записи",
    )

    body = models.TextField(
        null=True,
        blank=True,
        verbose_name="Запись",
        help_text="Введите запись",
    )

    video_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Ссылка на видео-материал",
        help_text="Введите ссылку на видео-материал",
    )


class ContentPayment(models.Model):
    """Модель оплаты контента"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя",
    )

    paid_content = models.ForeignKey(
        PaidContent,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Оплаченный контент",
        help_text="Введите оплаченный контент",
    )

    payment_amount = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name="Сумма к оплате",
        help_text="Введите сумму к оплате",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name="Дата оплаты",
        help_text="Введите дату оплаты",
    )

    session_id = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        verbose_name="id сессии",
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
        return f"{self.user} - {self.paid_content} - {self.payment_amount} - {self.created_at}"

    class Meta:
        verbose_name = "Покупка доступа к контенту"
        verbose_name_plural = "Покупки доступа к контенту"
        ordering = ["created_at"]


class BuyerSubscription(models.Model):
    """Модель подписки на оплаченный контент"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )

    content = models.ManyToManyField(
        PaidContent,
        verbose_name="Контент",
        help_text="Укажите контент",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Статус активности подписки",
        help_text="Укажите статус активности подписки",
    )

    class Meta:
        verbose_name = "Подписка на контент"
        verbose_name_plural = "Подписки на контент"
