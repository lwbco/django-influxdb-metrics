"""Loads celery or non-celery version."""
from django.conf import settings

try:
    from .tasks import write_points as write_points_celery
except ImportError:
    write_points_celery = None

from .utils import write_points as write_points_normal

write_points = None
if getattr(settings, 'INFLUXDB_USE_CELERY', False):
    write_points = write_points_celery.delay
else:
    write_points = write_points_normal

def log_startup():
    from .utils import build_tags
    data = [{
        'measurement': 'django_entrypoint',
        'tags': build_tags(),
        'fields': {'value': 1, },
    }]
    write_points(data)

if getattr(settings, 'INFLUXDB_LOG_ENTRYPOINT', True):
    log_startup()
