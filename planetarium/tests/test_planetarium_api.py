from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from planetarium.models import ShowTheme, AstronomyShow

SHOW_THEMES_URL = "/api/planetarium/show_themes/"


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.show_theme = ShowTheme.objects.create(name="Test Theme")
        self.astronomy_show = AstronomyShow.objects.create(
            title="Test Show", description="Test Description"
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def test_access_protected_endpoint(self):
        tokens = self.get_tokens_for_user(self.user)
        response = self.client.get(
            SHOW_THEMES_URL,
            HTTP_AUTHORIZATION=f"Bearer" f' {tokens["access"]}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        response = self.client.post(SHOW_THEMES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_token(self):
        response = self.client.get(
            SHOW_THEMES_URL,
            HTTP_AUTHORIZATION="Bearer " "InvalidToken",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
