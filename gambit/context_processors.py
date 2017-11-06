from django.conf import settings


def global_settings(request):
    return {
        'APPLICATION_VERSION': settings.APPLICATION_VERSION,
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'CONFERENCE_YEAR': settings.CONFERENCE_YEAR
    }
