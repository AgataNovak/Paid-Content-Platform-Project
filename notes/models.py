from django.db import models
from users.models import User


class PaidContent(models.Model):
    """Модель платной записи"""

    owner = models.ForeignKey(
        User,
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

    owner = models.ForeignKey(
        User,
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

    note_body = models.CharField(
        max_length=2000,
        default="Запись отсутствует",
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


class ContentSubscriptionPayment(models.Model):
    """Модель оплаты контента"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Пользователь",
        help_text="Введите пользователя"
    )

    paid_content = models.ManyToManyField(
        PaidContent,
        blank=False,
        null=False,
        verbose_name="Название оплаченного контента",
        help_text="Введите название оплаченного контента",
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


class BuyerSubscription(models.Model):
    """Модель подписки на оплаченный контент"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",

    )

    content = models.ManyToManyField(
        PaidContent,
        verbose_name="Контент",
        help_text="Укажите контент",
    )

    class Meta:
        verbose_name = "Подписка на контент"
        verbose_name_plural = "Подписки на контент"
