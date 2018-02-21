from django.urls import reverse
from django_webtest import WebTest
from django.test.utils import override_settings

from . import factories


class AuthenticationTest(WebTest):
    def setUp(self):
        self.user = factories.UserFactory.create()

    def tearDown(self):
        self.user.delete()

    def test_user_login_client(self):
        self.resp = self.client.login(username=self.user.username, password=factories.USER_PASSWORD)
        self.assertEqual(self.resp, True)
        self.client.logout()

    @override_settings(CSRF_COOKIE_SECURE=False, SESSION_COOKIE_SECURE=False)
    def test_user_login_view(self):
        login_view = self.app.get(reverse("login"))
        login_form = login_view.forms[0]
        login_form["username"] = self.user.username
        login_form["password"] = factories.USER_PASSWORD
        response = login_form.submit().follow()
        self.assertEqual(response.context["user"].username, self.user.username)
