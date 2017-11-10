from django.contrib import admin
from django.template import defaultfilters
from django.core.urlresolvers import reverse

from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'username',)

    def username(self, obj):
        return '<a href=\'{0!s}\'>{1!s}</a>'.format(reverse('admin:auth_user_change', args=(obj.user.id,)), obj.user.username)
    username.allow_tags = True
    username.short_description = 'User'


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'username', 'timestamp',)

    def username(self, obj):
        return '<a href=\'{0!s}\'>{1!s}</a>'.format(reverse('admin:auth_user_change', args=(obj.user.id,)), obj.user.username)
    username.allow_tags = True
    username.short_description = 'User'

    def timestamp(self, obj):
        return defaultfilters.date(obj.submitted_on, 'Y-m-d H:i')


class SubmissionReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'submitted_on', 'uuid_snip')

    def submission(self, obj):
        return obj.submission.title

    def reviewer(self, obj):
        return obj.user.username

    def uuid_snip(self, obj):
        return obj.uuid.hex
    uuid_snip.short_description = 'UUID'


class FrontPageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=FrontPage):
        return False


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(FrontPage, FrontPageAdmin)
admin.site.register(SubmissionReview, SubmissionReviewAdmin)
