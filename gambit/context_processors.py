from django.conf import settings

from .models import FrontPage


# Globally-accessible custom variables
# These all require matching declarations in settings.py
def global_settings(request):
    return {
        'APPLICATION_VERSION': settings.APPLICATION_VERSION,
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'CONFERENCE_YEAR': settings.CONFERENCE_YEAR,
        'SUBMISSION_DEADLINE': FrontPage.objects.filter(id=1)[0].submission_deadline,
    }
