from .base import *


try:
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
    DATABASES['default']['USER'] = os.environ["DJANGO_DATABASE_USER"]
    DATABASES['default']['PASSWORD'] = os.environ["DJANGO_DATABASE_PASSWORD"]
    DATABASES['default']['PORT'] = os.environ["DJANGO_DATABASE_PORT"]
except KeyError as e:
    print(f"\nEnvironment variable not set! {e!r}\n")
    raise SystemExit(1)
