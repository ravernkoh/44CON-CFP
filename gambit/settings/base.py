import os

import yaml


# Define application root directory [<project_root>/<application_root>/]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Collect user settings from config.yaml. If configuration file is unavailable, exit gracefully.
try:
    configuration = yaml.safe_load(open(os.path.join(BASE_DIR, "config.yaml")))
except FileNotFoundError:
    logger.error(f"[!!] Configuration file cannot be found. config.yaml should be present in {BASE_DIR!s}")
    raise SystemExit(1)

ALLOWED_HOSTS = [host for host in configuration["core"]["allowed_hosts"]]
DEBUG = configuration["core"]["debug"]
SECRET_KEY = configuration["core"]["secret_key"]
SESSION_COOKIE_SECURE = configuration["security"]["secure_cookies"]
CSRF_COOKIE_SECURE = configuration["security"]["secure_cookies"]
CSRF_USE_SESSIONS = configuration["security"]["csrf_in_session"]
CSRF_FAILURE_VIEW = "gambit.views.csrf_failure"

ROOT_URLCONF = "gambit.urls"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
WSGI_APPLICATION = "gambit.wsgi.application"

INSTALLED_APPS = [
    'gambit.apps.GambitConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'anymail',
]

if configuration["django_hijack"]["enabled"]:
    INSTALLED_APPS.append("hijack")
    INSTALLED_APPS.append("hijack_admin")
    INSTALLED_APPS.append("compat")
    HIJACK_LOGIN_REDIRECT_URL = "/profile/"
    HIJACK_LOGOUT_REDIRECT_URL = "/admin/auth/user/"
    HIJACK_USE_BOOTSTRAP = configuration["django_hijack"]["use_bootstrap"]
    HIJACK_ALLOW_GET_REQUESTS = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if configuration["minification"]["enabled"]:
    MIDDLEWARE.append("htmlmin.middleware.HtmlMinifyMiddleware")
    MIDDLEWARE.append("htmlmin.middleware.MarkRequestMiddleware")
    HTML_MINIFY = True
    INSTALLED_APPS.append("compressor")
    COMPRESS_OUTPUT_DIR = configuration["minification"]["compress_output_dir"]
    COMPRESS_OFFLINE = configuration["minification"]["compress_offline"]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'gambit.context_processors.global_settings',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gambit',
        'USER': configuration['database']['user'],
        'PASSWORD': configuration['database']['password'],
        'HOST': configuration['database']['host'],
        'PORT': configuration['database']['port'],
        'TEST': {
            'NAME': 'test_gambit'
        },
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format':   '%(levelname)s %(asctime)s %(module)s '
                        '%(process)d %(thread)d %(message)s',
        },
        'coloured_verbose': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)s %(bold_white)s[%(process)d] %(bold_blue)s%(message)s",
        },
    },
    'handlers': {
        'coloured_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'coloured_verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['coloured_console'],
        },
        'gunicorn.access': {
            'handlers': ['coloured_console'],
        },
        'gunicorn.error': {
            'handlers': ['coloured_console'],
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['coloured_console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['coloured_console'],
            'propagate': False,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': (
            "django.core.cache.backends.locmem.LocMemCache"
            if configuration["core"]["cache"] == "local"
            else "django.core.cache.backends.dummy.DummyCache"
        ),
    },
}

PASSWORD_HASHERS = [
    'gambit.hashers.ParanoidBCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': configuration["core"]["minimum_password_length"],
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../bower_components'),
    os.path.join(BASE_DIR, 'assets'),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    'MAILGUN_API_KEY': configuration["anymail"]["mailgun"]["api_key"],
    'MAILGUN_SENDER_DOMAIN': configuration["anymail"]["mailgun"]["sender_domain"],
}
DEFAULT_FROM_EMAIL = configuration['anymail']['from_email']

if configuration["sentry"]["enabled"]:
    import raven
    INSTALLED_APPS.append("raven.contrib.django.raven_compat")
    MIDDLEWARE.insert(1, "raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware")
    RAVEN_CONFIG = {
        'dsn': configuration['sentry']['dsn'],
        'release': raven.fetch_git_sha(os.path.join(BASE_DIR, os.pardir)),
    }

# Custom global variables
# These require matching declarations in context_processors.py
CONFERENCE_NAME = configuration["conference"]["name"]
CONFERENCE_YEAR = configuration["conference"]["year"]

# Whitelist of acceptable file types for submissions
CONTENT_TYPES = [ct for ct in configuration["whitelist_content_types"]]

# Maximum size in bytes of uploaded files for submissions
MAX_UPLOAD_SIZE = configuration["core"]["max_upload_size"]
