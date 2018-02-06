import factory
from django.contrib.auth import models
from django.contrib.auth.hashers import make_password


USER_PASSWORD = "loremipsumdolor"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = f"{first_name}.{last_name}"
    password = make_password(USER_PASSWORD)
    email = factory.LazyAttribute(lambda a: f"{a.first_name}.{a.last_name}@example.com".lower())
    is_active = True
    is_staff = False
    is_superuser = False
