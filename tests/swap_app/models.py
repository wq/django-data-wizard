from wq.db.patterns import models
from wq.db.contrib.vera.models import BaseSite, BaseReport

from django.conf import settings


class Site(models.IdentifiedModel, BaseSite):
    class Meta:
        abstract = not settings.SWAP


class Record(BaseReport):
    class Meta:
        abstract = not settings.SWAP
