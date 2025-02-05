from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import Payment

User = get_user_model()


class CustomUserTestCase(APITestCase):
    """Класс тестирования эндпоинтов модели CustomUser"""

    def setUp(self):
        pass

    def test_custom_user_create(self):
        data = {
            "username": "Test username 1",
            "phone_number": "89511234567",
        }
        url = reverse("users:register")
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BuySubscriptionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    @patch("stripe.PaymentIntent.retrieve")
    def test_buy_subscription_success(self, mock_retrieve):
        mock_retrieve.return_value = {"status": "succeeded"}  # Подготовка mock-ответа
        payment = Payment.objects.create(
            user=self.user,
            session_id="test_session_id",
            status="pending",
            payment_amount=10000,
        )
        response = self.client.post(reverse("users:service_subscribe"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.subscription)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/paid_content_list.html")

    @patch("stripe.PaymentIntent.retrieve")
    def test_buy_subscription_payment_already_exists(self, mock_retrieve):
        # Создаем платеж, который уже существует
        payment = Payment.objects.create(
            user=self.user,
            session_id="test_session_id",
            status="pending",
            payment_amount=10000,
        )
        mock_retrieve.return_value = {"status": "succeeded"}
        response = self.client.post(reverse("users:service_subscribe"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.subscription)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/paid_content_list.html")

    @patch("stripe.PaymentIntent.retrieve")
    def test_buy_subscription_payment_failed(self, mock_retrieve):
        payment = Payment.objects.create(
            user=self.user,
            session_id="test_session_id",
            status="pending",
            payment_amount=10000,
        )
        mock_retrieve.return_value = {"status": "failed"}
        response = self.client.post(reverse("users:service_subscribe"))
        self.assertFalse(self.user.subscription)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/buy_subscription.html")

    @patch("stripe.PaymentIntent.retrieve")
    def test_buy_subscription_payment_exception(self, mock_retrieve):
        payment = Payment.objects.create(
            user=self.user,
            session_id="test_session_id",
            status="pending",
            payment_amount=10000,
        )
        mock_retrieve.side_effect = Exception("Stripe error")
        response = self.client.post(reverse("users:service_subscribe"))
        self.assertFalse(self.user.subscription)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/buy_subscription.html")
