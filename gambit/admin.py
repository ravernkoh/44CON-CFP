import csv

from django.urls import reverse
from django.contrib import admin
from django.http import HttpResponse
from django.template import defaultfilters
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import (Profile, Submission, SubmissionReview, FrontPage, SubmissionDeadline, RegistrationStatus,
    HelpPageItem)


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        '_username',
    )
    search_fields = (
        'name',
        'user__username',
    )
    list_per_page = 25
    list_select_related = ('user',)

    # Renders the related username as a link to the edit page for the actual user object
    def _username(self, obj):
        link_to_user_object = reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe(f"<a href='{link_to_user_object}'>{obj.user.username}</a>")
    _username.short_description = "User"
    _username.admin_order_field = "user__username"  # Allows this field to be sortable


admin.site.register(Profile, ProfileAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        '_username',
    )
    list_filter = (
        'submitted_on',
    )
    readonly_fields = (
        'file_hash',
        '_timestamp',
    )
    actions = ['_export_to_csv']
    list_select_related = ('user',)
    list_per_page = 25
    search_fields = (
        'title',
        'user__username',
    )

    # Adds button in top right which will open the submission on the live site
    def view_on_site(self, obj):
        return reverse("submission", args=(obj.uuid,))

    # Renders the related username as a link to the edit page for the actual user object
    def _username(self, obj):
        link_to_user_object = reverse("admin:auth_user_change", args=(obj.user.id,))
        return mark_safe(f"<a href='{link_to_user_object}'>{obj.user.username}</a>")
    _username.short_description = "User"
    _username.admin_order_field = "user__username"  # Allows this field to be sortable

    # ISO 8601 date formatting or GTFO
    def _timestamp(self, obj):
        return defaultfilters.date(obj.submitted_on, "Y-m-d H:i")
    _timestamp.short_description = "Submitted on"

    def _export_to_csv(self, request, queryset):
        """I apologise for this horrendous method."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=44CON-CFP-submissions.csv"
        writer = csv.writer(response)
        writer.writerow(['Title', 'Authors', 'Contact', 'Submitted On', 'Score', 'Submitter', 'Submitter Email', 'Country',])
        submissions = queryset.values_list('title', 'authors', 'contact_email', 'submitted_on',)
        for index, submission in enumerate(submissions):
            # submission is iterated out to create a list instead of a tuple so that the score can be appended
            # I was lazy with this and there's probably a far more elegant way to do it
            submission = [field for field in submission]
            submission.append(queryset[index].get_average_score())
            submission.append(queryset[index].user.profile.name)
            submission.append(queryset[index].user.email)
            submission.append(queryset[index].user.profile.country)
            writer.writerow(submission)
        return response
    _export_to_csv.short_description = "Export to CSV"


admin.site.register(Submission, SubmissionAdmin)


class SubmissionReviewAdmin(admin.ModelAdmin):
    list_display = (
        '_submission',
        '_reviewer',
        'submitted_on',
    )
    list_filter = (
        'submitted_on',
    )
    actions = ['_export_to_csv']
    ordering = ["-submitted_on"]  # Descending order of submission
    list_select_related = (
        'user',
        'submission',
    )
    list_per_page = 25
    search_fields = (
        'submission__title',
        'user__username',
    )

    # Adds button in top right which will open the related submission on the live site
    def view_on_site(self, obj):
        return reverse("submission", args=(obj.submission.uuid,))

    def _submission(self, obj):
        return obj.submission.title
    _submission.admin_order_field = "submission__title"  # Allows this field to be sortable

    def _reviewer(self, obj):
        return obj.user.username
    _reviewer.admin_order_field = "user__username"  # Allows this field to be sortable

    def _export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=44CON-CFP-review-comments.csv"
        writer = csv.writer(response)
        writer.writerow(['Reviewer', 'Comments', 'Submission Title'])
        reviews = queryset.values_list('user__profile__name', 'comments', 'submission__title',)
        for review in reviews:
            writer.writerow(review)
        return response
    _export_to_csv.short_description = "Export to CSV"


admin.site.register(SubmissionReview, SubmissionReviewAdmin)


class FrontPageAdmin(admin.ModelAdmin):
    # This model is naively used to control the content display on the front page of the website
    # In later versions, this will be superceded by a content management system accessed through the website
    list_display = ('name',)

    # Prevents adding additional FrontPage objects from the admin UI
    # Can be overridden from the Django shell
    def has_add_permission(self, *args, **kwargs):
        return not FrontPage.objects.exists()


admin.site.register(FrontPage, FrontPageAdmin)


class SubmissionDeadlineAdmin(admin.ModelAdmin):
    # Naive object to handle deadline for submissions
    list_display = ('name',)

    # Prevents adding additional SubmissionDeadline objects from the admin UI
    # Can be overridden from the Django shell
    def has_add_permission(self, *args, **kwargs):
        return not SubmissionDeadline.objects.exists()


admin.site.register(SubmissionDeadline, SubmissionDeadlineAdmin)


class RegistrationStatusAdmin(admin.ModelAdmin):
    # Naive object to handle whether new users can be created
    list_display = ('name',)

    # Prevents adding additional RegistrationStatus objects from the admin UI
    # Can be overridden from the Django shell
    def has_add_permission(self, *args, **kwargs):
        return not RegistrationStatus.objects.exists()


admin.site.register(RegistrationStatus, RegistrationStatusAdmin)


class HelpPageItemAdmin(admin.ModelAdmin):
    # This model is naively used to control the content display on the help page of the website
    # In later versions, this will be superceded by a content management system accessed through the website
    list_display = ('name',)


admin.site.register(HelpPageItem, HelpPageItemAdmin)
