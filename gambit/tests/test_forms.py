from django.urls import reverse
from django.test import TestCase

from gambit.forms import SignUpForm, SubmitForm
from . import factories


class SignupFormBase(TestCase):
    def setUp(self):
        first_name = "Test"
        last_name = "User"
        self.name = f"{first_name} {last_name}"
        self.username = f"{first_name}.{last_name}"
        self.country = "United Kingdom"
        self.affiliation = "None"
        self.email = f"{self.username}@example.com"


class SignupFormCorrect(SignupFormBase):
    def test_signup_form_correct(self):
        form = SignUpForm(data={
            'username': self.username,
            'email': self.email,
            'password1': factories.USER_PASSWORD,
            'password2': factories.USER_PASSWORD,
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertTrue(form.is_valid())


class SignupFormIncorrect(SignupFormBase):
    def test_signup_form_blacklisted_username(self):
        form = SignUpForm(data={
            'username': 'admin',
            'email': self.email,
            'password1': factories.USER_PASSWORD,
            'password2': factories.USER_PASSWORD,
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors()[0], "This username is restricted or otherwise unavailable. Please pick another.")

    def test_signup_form_existing_username(self):
        new_user = factories.UserFactory.create(username="taken")
        form = SignUpForm(data={
            'username': 'taken',
            'email': self.email,
            'password1': factories.USER_PASSWORD,
            'password2': factories.USER_PASSWORD,
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors()[0], "Username already exists.")

    def test_signup_form_existing_email_address(self):
        new_user = factories.UserFactory.create(email="null@example.org")
        form = SignUpForm(data={
            'username': 'taken',
            'email': "null@example.org",
            'password1': factories.USER_PASSWORD,
            'password2': factories.USER_PASSWORD,
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors()[0], "Email address has already been used.")

    def test_signup_form_password1_mismatch(self):
        form = SignUpForm(data={
            'username': self.username,
            'email': self.email,
            'password1': 'incorrect',
            'password2': factories.USER_PASSWORD,
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ["The two password fields didn't match."])

    def test_signup_form_password2_mismatch(self):
        form = SignUpForm(data={
            'username': self.username,
            'email': self.email,
            'password1': factories.USER_PASSWORD,
            'password2': 'incorrect',
            'name': self.name,
            'country': self.country,
            'affiliation': self.affiliation,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ["The two password fields didn't match."])


class SubmitFormBase(TestCase):
    def setUp(self):
        self.title = "Test Title"
        self.abstract = "Test abstract"
        self.authors = "J. Bloggs"
        self.contact_email = "test@example.org"
        self.conflicts = None
        self.correct_file = "gambit/tests/sample_correct_file.pdf"
        self.incorrect_file = "gambit/tests/sample_incorrect_file.txt"


class SubmitFormCorrect(SubmitFormBase):
    def test_submit_form_correct(self):
        with open(self.correct_file, 'r') as f:
            form = SubmitForm(data={
                'title': self.title,
                'abstract': self.abstract,
                'authors': self.authors,
                'contact_email': self.contact_email,
                'conflicts': self.conflicts,
                'file': f,
            })
            self.failUnless(form.is_valid())

