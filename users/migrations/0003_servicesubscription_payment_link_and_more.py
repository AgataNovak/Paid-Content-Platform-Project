# Generated by Django 5.1.5 on 2025-01-27 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_customuser_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicesubscription",
            name="payment_link",
            field=models.URLField(
                blank=True,
                help_text="Введите ссылку на оплату подписки",
                null=True,
                verbose_name="Ссылка на оплату подписки",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(
                blank=True,
                help_text="Загрузите фото профиля пользователя",
                null=True,
                upload_to="users/avatars",
                verbose_name="Фото профиля пользователя",
            ),
        ),
    ]
