from .base import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CONFERENCE_YEAR = '2018'

AUTH_PASSWORD_VALIDATORS[0].update({'OPTIONS': { 'min_length': 12 }})
