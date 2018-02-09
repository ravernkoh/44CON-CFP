import factory
from django.contrib.auth import models
from django.contrib.auth.hashers import make_password

from gambit.models import Submission, SubmissionReview, ManagedContent


USER_PASSWORD = "loremipsumdolor"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User
        django_get_or_create = ('username',)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = f"{first_name}.{last_name}"
    password = make_password(USER_PASSWORD)
    email = factory.LazyAttribute(lambda a: f"{a.first_name}.{a.last_name}@example.com".lower())
    is_active = True
    is_staff = False
    is_superuser = False


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Submission

    user = UserFactory.create()
    title = "Submission Title"


class SubmissionReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubmissionReview

    submission = SubmissionFactory.create()
    user = UserFactory.create()


class ManagedContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ManagedContent

    name = "Managed Content"
