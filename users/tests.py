from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status


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
