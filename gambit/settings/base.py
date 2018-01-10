import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "aMRdU5mkpfT1lX9FGg4X^X$@gK#94@uGI4&19H*uUQy&D05qxj3vlY72R$M665Ko"  # Fake secret for development env

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gambit',
        'USER': 'gambit',
        'PASSWORD': 'gambit',
        'HOST': 'localhost',
        'PORT': '5433',
    },
}

ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": "mg.44con.com",
}

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = "cfp@44con.com"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 360  # type: integer - reminder because it will throw obscure TypeError and I won't remember why
CACHE_MIDDLEWARE_KEY_PREFIX = ""  # https://docs.djangoproject.com/en/2.0/topics/cache/#the-per-site-cache

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
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
LOGIN_REDIRECT_URL = "home"

# Custom global variables
# These require matching declarations in context_processors.py
APPLICATION_VERSION = "0.0.1-alpha"
APPLICATION_NAME = "44CON CFP"
CONFERENCE_YEAR = "2018"

# Whitelist of acceptable file types for submissions
CONTENT_TYPES = [
    'application/pdf',  # .pdf
    'application/msword',  # .doc, .dot
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/vnd.ms-powerpoint',  # .ppt, .pot, .pps, .ppa
    'application/zip',  # .zip
]

# Maximum size in bytes of uploaded files for submissions
MAX_UPLOAD_SIZE = 52428000  # 50MiB
