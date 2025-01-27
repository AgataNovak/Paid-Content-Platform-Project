from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from users.models import CustomUser
from notes.models import (
    FreeContent,
    PaidContent,
    ContentPayment,
    BuyerSubscription
)


class FreeContentTestCase(APITestCase):
    """Класс тестирования эндпоинтов модели FreeContent"""

    def setUp(self):
        self.user = CustomUser.objects.create(username='Alice Test', phone_number='89015148266')
        self.client.force_authenticate(user=self.user)
        self.free_content = FreeContent.objects.create(
            user=self.user,
            title='Test free content title 1',
            body='Test free content body 1'
        )

    def test_free_content_retrieve(self):
        url = reverse('notes:free_content_retrieve', args=[self.free_content.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_free_content_update(self):
        url = reverse("notes:free_content_update", args=(self.free_content.pk,))
        data = {
            "body": "Test update body for free content",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_free_content_delete(self):
        url = reverse("notes:free_content_destroy", args=[self.free_content.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_free_content_create(self):
        self.user = CustomUser.objects.create(username='Alice Test 2', phone_number='89015148265')
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test free content title 2',
            'body': 'Test free content body 2'
        }
        url = reverse('notes:free_content_create')
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaidContentTestCase(APITestCase):
    """Класс тестирования эндпоинтов модели PaidContent"""

    def setUp(self):
        self.user = CustomUser.objects.create(username='Alice 3 Test', phone_number='89015148266', subscription=True)
        self.client.force_authenticate(user=self.user)
        self.free_content = PaidContent.objects.create(
            user=self.user,
            title='Test paid content title 1',
            body='Test paid content body 1',
            price=100
        )

    def test_paid_content_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("notes:paid_content_update", args=(self.free_content.pk,))
        data = {
            "body": "Test update body for paid content",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_paid_content_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'user': self.user,
            'title': 'Test paid content title 2',
            'body': 'Test paid content body 2'
        }
        url = reverse('notes:paid_content_create')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


