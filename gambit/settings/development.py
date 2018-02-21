from .base import *


# Collect user settings from config.yaml. If configuration file is unavailable, exit gracefully.
try:
    configuration = yaml.safe_load(open(os.path.join(BASE_DIR, "config.yaml")))
except FileNotFoundError:
    print(f"[!!] Configuration file cannot be found. config.yaml should be present in {BASE_DIR!s}")
    raise SystemExit(1)

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

if configuration["minification"]["compress_in_debug"]:
    COMPRESS_ENABLED = True

if configuration["django_debug_toolbar"]["enabled"]:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(3, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [ip for ip in configuration["django_debug_toolbar"]["internal_ips"]]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
