# Generated by Django 5.1.5 on 2025-01-25 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="freecontent",
            name="note_body",
        ),
        migrations.AddField(
            model_name="freecontent",
            name="body",
            field=models.TextField(
                blank=True, help_text="Введите запись", null=True, verbose_name="Запись"
            ),
        ),
    ]
