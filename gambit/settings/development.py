from .base import *


DEBUG = True
COMPRESS_ENABLED = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
INTERNAL_IPS = ['127.0.0.1']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
