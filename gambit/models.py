import os
import uuid
import hashlib

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.core.validators import MaxValueValidator, MinValueValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        username = self.user.username
        return username

    def get_submissions(self):
        submissions = Submission.objects.filter(user=self.user)
        return submissions

    def get_reviews(self):
        reviews = SubmissionReview.objects.filter(user=self.user)
        return reviews


    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# During user signup, a linked profile object is tied to the generated user object
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    submitted_on = models.DateTimeField(db_index=True, auto_now_add=True)
    title = models.CharField(max_length=255)
    authors = models.TextField(blank=True)
    contact_email = models.EmailField()
    abstract = models.TextField(blank=True)
    conflicts = models.TextField(blank=True)
    file = models.FileField(upload_to="uploads/submissions/%Y/%m/%d/", blank=True)
    file_hash = models.CharField(max_length=128, blank=True)
    review_count = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    total_score = models.IntegerField(default=0)
    average_expertise_score = models.FloatField(default=0)
    total_expertise_score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.file:
            sha512 = hashlib.sha512()
            for chunk in self.file.chunks():
                sha512.update(chunk)
            self.file_hash = sha512.hexdigest()
        super(Submission, self).save(*args, **kwargs)

    def __str__(self):
        title = f"{self.title!s}"
        return title

    def get_reviews(self):
        reviews = SubmissionReview.objects.filter(submission=self)
        return reviews
    
    def has_reviewed(self, user_id):
        # Returns True if supplied user_id matches review for submission
        reviews = [review.user.id for review in self.get_reviews()]
        return user_id in reviews

    def get_average_score(self):
        reviews = self.get_reviews()
        average_score = reviews.aggregate(models.Avg("submission_score"))["submission_score__avg"] or 0
        return float(f"{average_score:.2f}")

    def get_total_score(self):
        reviews = self.get_reviews()
        total_score = reviews.aggregate(models.Sum("submission_score"))["submission_score__sum"]
        return total_score or 0

    def get_file_name(self):
        if self.file:
            _, tail = os.path.split(self.file.name)  # Discarding path prefix
            return tail

    def get_related_submissions(self):
        return Submission.objects.filter(user=self.user).exclude(uuid=self.uuid).values('uuid', 'user__id', 'title', 'submitted_on')


    class Meta:
        ordering = ["submitted_on"]
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"


class SubmissionReview(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    submitted_on = models.DateTimeField(db_index=True, auto_now_add=True)
    expertise_score = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    submission_score = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    comments = models.TextField(blank=True)

    def __str__(self):
        uuid = f"{self.uuid!s}"
        return uuid

    def get_reviewer_name(self):
        user_id = self.user_id
        profile = Profile.objects.get(user_id=user_id)
        name = profile.name
        return name


    class Meta:
        ordering = ["submitted_on"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


def update_submission(submission):
    submission.review_count = SubmissionReview.objects.filter(submission=submission).count()
    submission.average_score = float("{0:.2f}".format(submission.get_reviews().aggregate(models.Avg("submission_score"))["submission_score__avg"] or 0))
    submission.average_expertise_score = float("{0:.2f}".format(submission.get_reviews().aggregate(models.Avg("expertise_score"))["expertise_score__avg"] or 0))
    submission.total_score = submission.get_reviews().aggregate(models.Sum("submission_score"))["submission_score__sum"] or 0
    submission.total_expertise_score = submission.get_reviews().aggregate(models.Sum("expertise_score"))["expertise_score__sum"] or 0
    submission.save()

@receiver(post_save, sender=SubmissionReview, dispatch_uid="update_submission_details_save")
def update_submission_save(sender, instance, **kwargs):
    submission = instance.submission
    update_submission(submission)

@receiver(post_delete, sender=SubmissionReview, dispatch_uid="update_submission_details_delete")
def update_submission_delete(sender, instance, **kwargs):
    submission = instance.submission
    update_submission(submission)


class ManagedContent(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        name = self.name
        return name


class SubmissionDeadline(ManagedContent):
    open_date = models.DateTimeField(default=timezone.now)
    close_date = models.DateTimeField(default=timezone.now)
    message = models.TextField(blank=True)


    class Meta:
        verbose_name = "Submission Deadline"
        verbose_name_plural = "Submission Deadline"


class RegistrationStatus(ManagedContent):
    disabled = models.BooleanField(default=True)


    class Meta:
        verbose_name = "Registration Status"
        verbose_name_plural = "Registration Status"


class FrontPage(ManagedContent):
    leading_paragraph = models.TextField(blank=True)
    submission_paragraph = models.TextField(blank=True)
    speaker_paragraph = models.TextField(blank=True)
    important_dates = models.TextField(blank=True)
    alert = models.TextField(blank=True)


    class Meta:
        verbose_name = "Front Page"
        verbose_name_plural = "Front Page"


class HelpPageItem(ManagedContent):
    title = models.CharField(max_length=255)
    content = models.TextField()


    class Meta:
        verbose_name = "Help Page"
        verbose_name_plural = "Help Page"
