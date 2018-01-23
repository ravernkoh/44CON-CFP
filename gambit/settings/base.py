import os

import yaml


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    configuration = yaml.safe_load(open(os.path.join(BASE_DIR, "config.yaml")))
except FileNotFoundError:
    raise SystemExit("\nConfiguration file cannot be found. config.yaml should be present in <project root>/gambit/\n")

try:
    SECRET_KEY = configuration['core']['secret_key']
except TypeError:
    raise SystemExit("\nSecret key has not been set. Please review config.yaml\n")

ALLOWED_HOSTS = "*"
DEBUG = False

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "gambit.urls"

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

WSGI_APPLICATION = "gambit.wsgi.application"

try:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'gambit',
            'USER': configuration['postgresql']['user'],
            'PASSWORD': configuration['postgresql']['password'],
            'HOST': 'localhost',
            'PORT': configuration['postgresql']['port'],
        },
    }
except KeyError as e:
    raise SystemExit(f"\nPostgresql {e!s} has not been set. Please review config.yaml\n")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
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
    },
}

try:
    ANYMAIL = {
        "MAILGUN_API_KEY": configuration['anymail']['mailgun']['api_key'],
        "MAILGUN_SENDER_DOMAIN": configuration['anymail']['mailgun']['sender_domain'],
    }
except KeyError as e:
    print(f"\nEnvironment variable not set! {e!r}\n")
    raise SystemExit(1)

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
try:
    DEFAULT_FROM_EMAIL = configuration['anymail']['from_email']
except TypeError:
    raise SystemExit("\nDefault 'from' email has not been set. Please review config.yaml\n")

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
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
            'min_length': 12,
        },
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../bower_components'),
    os.path.join(BASE_DIR, 'assets')
]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
LOGIN_REDIRECT_URL = "home"

# Custom global variables
# These require matching declarations in context_processors.py
APPLICATION_VERSION = "0.0.1-beta"
APPLICATION_NAME = "44CON CFP"
CONFERENCE_YEAR = "2018"

# Whitelist of acceptable file types for submissions
CONTENT_TYPES = [
    'application/pdf',  # .pdf
    'application/msword',  # .doc, .dot
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/vnd.ms-powerpoint',  # .ppt, .pot, .pps, .ppa
]

# .zip files can suck it. Why do you not have one universal identifier?
# Putting these here instead of directly into the CONTENT_TYPES so I know what they're all for
# Don't judge me
CONTENT_TYPES.extend([
    'application/zip',
    'application/x-zip',
    'application/octet-stream',
    'application/x-zip-compressed'
])

# Maximum size in bytes of uploaded files for submissions
MAX_UPLOAD_SIZE = 52428000  # 50MiB
