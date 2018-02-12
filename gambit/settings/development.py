from .base import *


DEBUG = True
COMPRESS_ENABLED = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
