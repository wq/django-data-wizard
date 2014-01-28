from wq.db.patterns import models
from wq.db.contrib.vera.models import BaseSite, BaseReport


class Site(models.IdentifiedModel, BaseSite):
    pass


class Report(BaseReport):
    pass
