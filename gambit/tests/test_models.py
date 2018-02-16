import random
from django.db import models
from django.test import TestCase
from django.contrib.auth.models import User

from . import factories
from gambit.models import SubmissionReview


class ProfileModel(TestCase):
    def setUp(self):
        self.user = factories.UserFactory.create()

    def tearDown(self):
        self.user.delete()

    def test_profile__str__(self):
        self.assertEqual(self.user.profile.__str__(), self.user.username)


class SubmissionModel(TestCase):
    def setUp(self):
        self.submission = factories.SubmissionFactory.create()
        generate_reviews = lambda x,y: factories.SubmissionReviewFactory.create(submission=self.submission, expertise_score=x, submission_score=y)
        for i in range(5):
            generate_reviews(random.randint(0,5), random.randint(0,5))

    def tearDown(self):
        self.submission.delete()
        for each in self.submission.get_reviews():
            each.delete()

    def test_submission__str__(self):
        self.assertEqual(self.submission.__str__(), self.submission.title)

    def test_submission_get_reviews(self):
        qs = SubmissionReview.objects.filter(submission=self.submission)
        self.assertQuerysetEqual(self.submission.get_reviews(), map(repr, qs))

    def test_submission_get_average_score(self):
        avg_score = SubmissionReview.objects.filter(submission=self.submission).aggregate(models.Avg("submission_score"))["submission_score__avg"]
        self.assertEqual(self.submission.get_average_score(), avg_score)

    def test_submission_get_total_score(self):
        total_score = SubmissionReview.objects.filter(submission=self.submission).aggregate(models.Sum("submission_score"))["submission_score__sum"]
        self.assertEqual(self.submission.get_total_score(), total_score)


class SubmissionReviewModel(TestCase):
    def setUp(self):
        self.submission_review = factories.SubmissionReviewFactory.create()

    def tearDown(self):
        self.submission_review.delete()

    def test_submission_review__str__(self):
        self.assertEqual(self.submission_review.__str__(), f"{self.submission_review.uuid!s}")


class ManagedContentModel(TestCase):
    def setUp(self):
        self.managed_content = factories.ManagedContentFactory.create()

    def tearDown(self):
        self.managed_content.delete()

    def test_submission_review__str__(self):
        self.assertEqual(self.managed_content.__str__(), self.managed_content.name)
