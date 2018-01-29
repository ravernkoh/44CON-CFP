from django.conf import settings

from .models import SubmissionDeadline

deadline = SubmissionDeadline.objects.first()


# Globally-accessible custom variables
# These all require matching declarations in settings.py
def global_settings(request):
    return {
        'APPLICATION_VERSION': settings.APPLICATION_VERSION,
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'CONFERENCE_YEAR': settings.CONFERENCE_YEAR,
        'RELEASE_HASH': settings.RAVEN_CONFIG['release'],
        'SUBMISSION_DEADLINE': deadline.date if deadline else None,
    }
