"""Loads celery or non-celery version."""
from django.conf import settings

import time

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


def log_metric(measurement, fields=None, tags=None):
    from .utils import build_tags
    data = [{
        'measurement': measurement,
        'fields': fields or {'value': 1},
        'tags': build_tags(tags),
    }]
    return write_points(data)


class TimingMetric(object):
    def __init__(self, measurement, tags=None):
        self.measurement = measurement
        self.fields = {'count': 1}
        self.tags = tags or {}

    def __enter__(self):
        self.start_time = time.time()
        self.stop_time = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_time = time.time()
        self.fields['value'] = self.elapsed
        self.tags['success'] = str(bool(exc_type))
        self.tags['exception'] = str(exc_type or '')
        log_metric(self.measurement, self.fields, self.tags)

    @property
    def elapsed(self):
        return (self.stop_time or time.time()) - self.start_time


if getattr(settings, 'INFLUXDB_LOG_ENTRYPOINT', True):
    log_metric('django_entrypoint')
