from django.test import TestCase

from . import factories
from gambit.tokens import account_activation_token


class AccountActivationTokenGeneratorTest(TestCase):
    def setUp(self):
        self.user = factories.UserFactory.create()
        self.token = account_activation_token.make_token(self.user)

    def tearDown(self):
        self.user.delete()

    def test_account_activation_token_generator(self):
        self.assertTrue(account_activation_token.check_token(self.user, self.token))
