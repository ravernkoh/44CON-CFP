from .base import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CONFERENCE_YEAR = '2018'

# Set minimum password length
AUTH_PASSWORD_VALIDATORS[0].update({'OPTIONS': { 'min_length': 12 }})

CONTENT_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
# 2MiB = 2621440
# 5MiB = 5242880
# 10MiB = 10485760
# 15MiB = 15728640
MAX_UPLOAD_SIZE = 5242880
