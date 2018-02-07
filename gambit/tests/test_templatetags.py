from django.test import TestCase
from django.template import Context, Template
from django.contrib.auth.models import Group

from . import factories


class HasGroup(TestCase):
    TEMPLATE = Template("{% load has_group %}{% if user|has_group:'test_group' %}Success{% endif %}")

    def setUp(self):
        test_group, created = Group.objects.get_or_create(name="test_group")
        self.user = factories.UserFactory.create()
        self.user.groups.add(test_group)

    def tearDown(self):
        self.user.delete()

    def test_has_group_permission(self):
        rendered = self.TEMPLATE.render(Context({'user': self.user}))
        self.assertIn(rendered, "Success")
