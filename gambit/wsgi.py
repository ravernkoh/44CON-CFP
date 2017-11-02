from os import environ, path as ospath
from sys import path as syspath

from django.core.wsgi import get_wsgi_application


environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
