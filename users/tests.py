from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from users.forms import UserRegisterForm
from users.views import get_access_key, refresh_access_key


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_valid_form(self):
        # Prepare valid form data
        form_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password1": "TestPass12345",
            "password2": "TestPass12345",
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse("register"), data=form_data)

        # Assert that the user is redirected to the login page
        self.assertRedirects(response, reverse("login"))
        #
        # # Assert success message is displayed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Your account has been created! Please check your "
            "email to verify your account before logging in.",
        )

    def test_register_existing_email(self):
        # Create a user with the same email as in the form
        User.objects.create_user(
            username="existinguser",
            email="existinguser@example.com",
            password="Testpass12345",
        )
        # Prepare form data
        form_data = {
            "username": "existinguser",
            "email": "existinguser@example.com",
            "password1": "Testpass12345",
            "password2": "Testpass12345",
        }
        form = UserRegisterForm(data=form_data)

        self.assertFalse(form.is_valid())

        # Assert that the form errors contain the expected error message
        expected_error = "A user with that username already exists."
        self.assertIn(expected_error, form.errors["username"])


class TestAPI(TestCase):
    def setUp(self):
        self.client = Client()
        mock_oauth_post = patch("users.views.call_c2_oauth_api")
        self.mock_oauth_post = mock_oauth_post.start()
        mock_get_access_key = patch("users.views.get_access_key")
        self.mock_get_access_key = mock_get_access_key.start()
        mock_refresh_access_key = patch("users.views.refresh_access_key")
        self.mock_refresh_access_key = mock_refresh_access_key.start()
        self.request = RequestFactory().get("/")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.request.user = self.user
        self.client.login(username="testuser", password="testpass")
        self.auth_code = "testcode"  # Replace with a valid auth code for
        # self.addCleanup(self.mock_oauth_post.stop)
        # self.addCleanup(mock_get_access_key.stop)
        # testing

    def test_get_access_key(self):
        mock_ret_data = {
            "access_token": "TestAccessKEY",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "TestRefresherToken",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ret_data
        self.mock_oauth_post.return_value = mock_response

        response_data = get_access_key(self.request, "TestCode")
        assert "access_token" in response_data.json()
        assert response_data.json()["access_token"] == mock_ret_data["access_token"]
        assert self.mock_oauth_post.called

    def test_refresh_access_key(self):
        mock_ret_data = {
            "access_token": "TestAccessKEY",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "TestRefresherToken",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ret_data
        self.mock_oauth_post.return_value = mock_response

        response_data = refresh_access_key(self.request)
        assert "access_token" in response_data.json()
        assert response_data.json()["access_token"] == mock_ret_data["access_token"]
        assert self.mock_oauth_post.called

    def test_oauth_with_c2_initial(self):
        mock_ret_data = {
            "access_token": "TestAccessKEY",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "TestRefresherToken",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ret_data
        self.mock_get_access_key.return_value = mock_response

        # Simulate the user not having a c2_api_key
        self.user.profile.c2_api_key = None
        self.user.profile.save()

        response = self.client.get("/oauth_with_c2")
        messages = list(response.wsgi_request._messages)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(messages[0]), "Your C2 API key has been saved")
        self.assertTemplateUsed(response, "users/profile.html")

    def test_oauth_with_c2_refresh(self):
        mock_ret_data = {
            "access_token": "TestAccessKEY",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "TestRefresherToken",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ret_data
        self.mock_refresh_access_key.return_value = mock_response

        # Simulate the user not having a c2_api_key
        self.user.profile.c2_api_key = "TestAPIKey"
        self.user.profile.save()

        response = self.client.get("/oauth_with_c2")
        messages = list(response.wsgi_request._messages)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(messages[0]), "Your C2 API key has been refreshed")
        self.assertTemplateUsed(response, "users/profile.html")
