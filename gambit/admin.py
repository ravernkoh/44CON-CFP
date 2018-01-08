from django.contrib import admin
from django.template import defaultfilters
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sessions.models import Session

from .models import Profile, Submission, SubmissionReview, FrontPage, HelpPageItem


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', '_username',)

    # Renders the related username as a link to the edit page for the actual user object
    def _username(self, obj):
        link_to_user_object = reverse('admin:auth_user_change', args=(obj.user.id,))
        return f"<a href='{link_to_user_object}'>{obj.user.username}</a>"
    _username.allow_tags = True  # Allow HTML tags in the field
    _username.short_description = 'User'


admin.site.register(Profile, ProfileAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', '_username', '_timestamp',)
    list_filter = ('user__username', 'submitted_on',)

    # Adds button in top right which will open the submission on the live site
    def view_on_site(self, obj):
        return reverse('submission', args=(obj.uuid,))

    # Renders the related username as a link to the edit page for the actual user object
    def _username(self, obj):
        link_to_user_object = reverse('admin:auth_user_change', args=(obj.user.id,))
        return f"<a href='{link_to_user_object}'>{obj.user.username}</a>"
    _username.allow_tags = True  # Allow HTML tags in the field
    _username.short_description = 'User'

    # ISO 8601 date formatting or GTFO
    def _timestamp(self, obj):
        return defaultfilters.date(obj.submitted_on, 'Y-m-d H:i')


admin.site.register(Submission, SubmissionAdmin)


class SubmissionReviewAdmin(admin.ModelAdmin):
    list_display = ('_submission', '_reviewer', 'submitted_on', '_uuid_snip',)
    list_filter = ('user__username', 'submitted_on',)

    # Adds button in top right which will open the related submission on the live site
    def view_on_site(self, obj):
        return reverse('submission', args=(obj.submission.uuid,))

    def _submission(self, obj):
        return obj.submission.title

    def _reviewer(self, obj):
        return obj.user.username

    # Print the stripped hexadecimal of the object UUID for simple reference
    # Provides no functional benefit but is useful for debugging
    # Can be removed completely in production environment
    def _uuid_snip(self, obj):
        return obj.uuid.hex
    _uuid_snip.short_description = 'UUID'


admin.site.register(SubmissionReview, SubmissionReviewAdmin)


class FrontPageAdmin(admin.ModelAdmin):
    # This model is naively used to control the content display on the front page of the website
    # In later versions, this will be superceded by a content management system accessed through the website
    list_display = ('__str__', 'id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=FrontPage):
        return False


admin.site.register(FrontPage, FrontPageAdmin)


class HelpPageItemAdmin(admin.ModelAdmin):
    # This model is naively used to control the content display on the help page of the website
    # In later versions, this will be superceded by a content management system accessed through the website
    list_display = ('short_description', 'id',)


admin.site.register(HelpPageItem, HelpPageItemAdmin)


class SessionAdmin(admin.ModelAdmin):
    # This model is exposed for debugging and troubleshooting purposes
    # Can be removed in production environment
    list_display = ('session_key', '_username', '_session_data', 'expire_date',)
    exclude = ('session_data',)
    readonly_fields = ('session_key', '_session_data',)

    # Unpickle the dictionary value containing the session data
    def _session_data(self, obj):
        return obj.get_decoded()
    _session_data.short_description = 'Session Data'

    def _username(self, obj):
        user_id = obj.get_decoded()['_auth_user_id']
        return User.objects.get(id=user_id)
    _username.short_description = 'Username'

    # Explicitly restrict manual session creation
    def has_add_permission(self, request):
        return False


admin.site.register(Session, SessionAdmin)
