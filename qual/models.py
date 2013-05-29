from wq.db.patterns import models
from wq.db.patterns.base import swapper
from django.conf import settings

MODELS = {
    model: swapper.is_swapped('qual', model) or model
    for model in ('Site', 'Event', 'Report', 'ReportStatus')
}

# Base classes for Site-Event-Report-Attribute-Value pattern
# Extend these when swapping out default implementation (below)

class BaseSite(models.NaturalKeyModel):
    class Meta:
        abstract = True

class BaseEvent(models.NaturalKeyModel):
    site = models.ForeignKey(MODELS['Site'])
    class Meta:
        abstract = True

class BaseReport(models.AnnotatedModel):
    event = models.ForeignKey(MODELS['Event']) 
    entered = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.ForeignKey(MODELS['ReportStatus'])

    def __unicode__(self):
        return "%s according to %s" % (self.event, self.user)

    class Meta:
        abstract = True

class BaseReportStatus(models.Model):
    name = models.CharField(max_length=255)
    is_valid = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class BaseParameter(models.BaseAnnotationType, models.IdentifiedModel):
    is_numeric = models.BooleanField()
    units = models.CharField(max_length=50, null=True, blank=True)

    @property
    def annotated_model(self):
        return swapper.load_model('qual', 'Report') 

    def __unicode__(self):
        if self.units:
             return "%s (%s)" % (self.name, self.units)
        else:
             return self.name
    class Meta:
        abstract = True
   
class BaseResult(models.BaseAnnotation):
    value_numeric = models.FloatField(null=True, blank=True)
    value_text = models.TextField(null=True, blank=True)

    @property
    def value(self):
        if self.value_numeric is not None:
            return self.value_numeric
        return self.value_text

    class Meta:
        abstract = True

# Default implementation of the above classes, can be swapped
class Site(BaseSite):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return "%s, %s" % (round(self.latitude, 3), round(self.longitude, 3))

    class Meta(BaseEvent.Meta):
        db_table = 'wq_site'
        swappable = swapper.swappable_setting('qual', 'Site')
        unique_together = ('latitude', 'longitude')
    
class Event(BaseEvent):
    date = models.DateField()
    
    def __unicode__(self):
        return "%s on %s" % (self.site, self.date)

    class Meta(BaseEvent.Meta):
        db_table = 'wq_event'
        swappable = swapper.swappable_setting('qual', 'Event')
        unique_together = ('site', 'date')

class Report(BaseReport):
    class Meta(BaseReport.Meta):
        db_table = 'wq_report'
        swappable = swapper.swappable_setting('qual', 'Report')

class ReportStatus(BaseReportStatus):
    class Meta(BaseReportStatus.Meta):
        verbose_name_plural = 'report statuses'
        db_table = 'wq_reportstatus'
        swappable = swapper.swappable_setting('qual', 'ReportStatus')

# These will be inactive unless they are explicitly swapped for annotate's equivalents
class Parameter(BaseParameter):
    class Meta(BaseParameter.Meta):
        db_table = 'wq_parameter'
        abstract = not (swapper.is_swapped('annotate', 'AnnotationType') == 'qual.Parameter')

class Result(BaseResult):
    class Meta(BaseResult.Meta):
        db_table = 'wq_result'
        abstract = not (swapper.is_swapped('annotate', 'Annotation') == 'qual.Result')
