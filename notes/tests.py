from django.contrib.auth import get_user_model
from notes.models import FreeContent, PaidContent, BuyerSubscription, ContentPayment
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

User = get_user_model()


class FreeContentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_free_content_creation(self):
        content = FreeContent.objects.create(
            user=self.user,
            title="Test Free Content",
            body="This is a test body.",
            video_link="http://example.com/video",
        )
        self.assertEqual(content.user, self.user)
        self.assertEqual(content.title, "Test Free Content")
        self.assertEqual(content.body, "This is a test body.")
        self.assertEqual(content.video_link, "http://example.com/video")


class FreeContentViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.free_content = FreeContent.objects.create(
            user=self.user,
            title="Test Free Content",
            body="This is a test body.",
            video_link="http://example.com/video",
        )

    def test_free_content_create_view(self):
        response = self.client.post(
            reverse("notes:free_content_create"),
            {
                "title": "New Free Content",
                "body": "This is a new free content.",
                "video_link": "http://example.com/new_video",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(FreeContent.objects.filter(title="New Free Content").exists())

    def test_free_content_detail_view(self):
        response = self.client.get(
            reverse("notes:free_content_retrieve", args=[self.free_content.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.free_content.title)

    def test_free_content_update_view(self):
        response = self.client.post(
            reverse("notes:free_content_update", args=[self.free_content.id]),
            {
                "title": "Updated Free Content",
                "body": "This is an updated body.",
                "video_link": "http://example.com/updated_video",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.free_content.refresh_from_db()
        self.assertEqual(self.free_content.title, "Updated Free Content")

    def test_free_content_delete_view(self):
        response = self.client.post(
            reverse("notes:free_content_destroy", args=[self.free_content.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(FreeContent.objects.filter(id=self.free_content.id).exists())

    def test_free_content_list_view(self):
        response = self.client.get(reverse("notes:free_content_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.free_content.title)


class PaidContentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.paid_content = PaidContent.objects.create(
            user=self.user,
            title="Test Paid Content test",
            body="Test body for paid content.",
            price=10000,
        )

    def test_paid_content_detail(self):
        """Тестирование получения деталей платного контента"""
        BuyerSubscription.objects.create(user=self.user, content=self.paid_content)
        response = self.client.get(
            reverse("notes:paid_content_retrieve", args=[self.paid_content.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Paid Content")

    def test_update_paid_content(self):
        """Тестирование обновления платного контента"""
        response = self.client.post(
            reverse("notes:paid_content_update", args=[self.paid_content.id]),
            {
                "title": "Updated Paid Content",
                "body": "Updated body for paid content.",
                "price": 2000,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.paid_content.refresh_from_db()
        self.assertEqual(self.paid_content.title, "Updated Paid Content")

    def test_delete_paid_content(self):
        """Тестирование удаления платного контента"""
        response = self.client.post(
            reverse("notes:paid_content_destroy", args=[self.paid_content.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PaidContent.objects.filter(id=self.paid_content.id).exists())

    def test_create_paid_content(self):
        """Тестирование создания платного контента"""
        response = self.client.post(
            reverse("notes:paid_content_create"),
            {
                "title": "New Paid Content",
                "body": "Body of new paid content.",
                "price": 1500,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PaidContent.objects.filter(title="New Paid Content").exists())

    def test_paid_content_list(self):
        """Тестирование получения списка платного контента"""
        response = self.client.get(reverse("notes:paid_content_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Paid Content")


class BuyContentSubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.content = PaidContent.objects.create(
            user=self.user, title="Test Content", price=1000
        )
        assert self.content.id is not None, "Content ID should not be None"

    @patch("stripe.PaymentIntent.retrieve")
    def test_buy_content_subscription_success(self, mock_retrieve):
        mock_retrieve.return_value = {"status": "succeeded"}
        self.assertIsNotNone(self.content.id, "Content ID should not be None")
        payment = ContentPayment.objects.create(
            user=self.user, paid_content=self.content, session_id="test_session_id"
        )
        response = self.client.post(
            reverse("notes:buy_paid_content", kwargs={"pk": self.content.id})
        )
        self.user.refresh_from_db()
        payment.refresh_from_db()
        self.assertTrue(self.user.subscription, "User subscription should be True")
        self.assertEqual(payment.status, "paid")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/paid_content_detail.html")
