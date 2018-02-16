from django.conf import settings

from .models import SubmissionDeadline


# Globally-accessible custom variables
# These all require matching declarations in settings.py
def global_settings(request):
    deadline = SubmissionDeadline.objects.first()
    try:
        release_hash = settings.RAVEN_CONFIG['release']
    except AttributeError:
        release_hash = None
    return {
        'CONFERENCE_NAME': settings.CONFERENCE_NAME,
        'CONFERENCE_YEAR': settings.CONFERENCE_YEAR,
        'RELEASE_HASH': release_hash,
        'SUBMISSION_DEADLINE': deadline.date if deadline else None,
    }
