from .base import *  # noqa: F403

DEBUG = False

# ManifestStaticFilesStorage is recommended in production, to prevent
# outdated JavaScript / CSS assets being served from cache
# (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/6.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES["staticfiles"][  # noqa: F405
    "BACKEND"
] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
