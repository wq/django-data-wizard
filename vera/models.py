from wq.db.patterns import models
from wq.db.patterns.base import swapper
from django.conf import settings
from collections import OrderedDict

MODELS = {
    model: swapper.is_swapped('vera', model) or model
    for model in ('Site', 'Event', 'Report', 'ReportStatus')
}

VALID_REPORT_ORDER = getattr(settings, "WQ_VALID_REPORT_ORDER", ('-entered',))
# Base classes for Site-Event-Report-Attribute-Value pattern
# Extend these when swapping out default implementation (below)

class BaseSite(models.NaturalKeyModel):
    class Meta:
        abstract = True

class BaseEvent(models.NaturalKeyModel):
    site = models.ForeignKey(MODELS['Site'])

    @property
    def valid_reports(self):
        return self.report_set.filter(status__is_valid=True).order_by(*VALID_REPORT_ORDER)

    @property
    def vals(self):
        vals = OrderedDict()
        for report in reversed(self.valid_reports):
            vals.update(report.vals)
        return vals

    @property
    def annotations(self):
        return [{
            'name': key,
            'value': val,
          } for key, val in self.vals.items()
            if val is not None and not (
              isinstance(val, basestring) and val.strip() != ''
            )
        ]
    
    class Meta:
        abstract = True

class ReportManager(models.Manager):
    def create_report(self, event_key, values, **kwargs):
        Event = swapper.load_model('vera', 'Event')
        kwargs['event'] = Event.objects.find(*event_key)
        report = self.create(**kwargs)
        report.vals = values
        return report

class ValidReportManager(ReportManager):
    def get_queryset(self):
        qs = super(ValidReportManager, self)
        return qs.filter(status__is_valid=True).order_by(*VALID_REPORT_ORDER)

class BaseReport(models.AnnotatedModel):
    event = models.ForeignKey(MODELS['Event'])
    entered = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.ForeignKey(MODELS['ReportStatus'], null=True, blank=True)

    objects = ReportManager()
    valid_objects = ValidReportManager()

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

class ParameterManager(models.IdentifiedRelatedModelManager,
                       models.AnnotationTypeManager):
    pass

class BaseParameter(models.IdentifiedRelatedModel, models.BaseAnnotationType):
    is_numeric = models.BooleanField()
    units = models.CharField(max_length=50, null=True, blank=True)

    objects = ParameterManager()

    @property
    def annotated_model(self):
        return swapper.load_model('vera', 'Report') 

    def __unicode__(self):
        if self.units:
             return u"%s (%s)" % (self.name, self.units)
        else:
             return self.name
    class Meta:
        abstract = True
   
class BaseResult(models.BaseAnnotation):
    value_numeric = models.FloatField(null=True, blank=True)
    value_text = models.TextField(null=True, blank=True)

    @property
    def value(self):
        if self.type.is_numeric:
            return self.value_numeric
        return self.value_text

    @value.setter
    def value(self, val):
        if self.type.is_numeric:
            if isinstance(val, basestring) and len(val.strip()) == 0:
                self.value_numeric = None
            else:
                self.value_numeric = val
        else:
            self.value_text = val

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
        swappable = swapper.swappable_setting('vera', 'Site')
        unique_together = ('latitude', 'longitude')
    
class Event(BaseEvent):
    date = models.DateField()
    
    def __unicode__(self):
        return "%s on %s" % (self.site, self.date)

    class Meta(BaseEvent.Meta):
        db_table = 'wq_event'
        swappable = swapper.swappable_setting('vera', 'Event')
        unique_together = ('site', 'date')
        ordering = ('-date',)

class Report(BaseReport):
    class Meta(BaseReport.Meta):
        db_table = 'wq_report'
        swappable = swapper.swappable_setting('vera', 'Report')

class ReportStatus(BaseReportStatus):
    class Meta(BaseReportStatus.Meta):
        verbose_name_plural = 'report statuses'
        db_table = 'wq_reportstatus'
        swappable = swapper.swappable_setting('vera', 'ReportStatus')

# These will be inactive unless they are explicitly swapped for annotate's equivalents
class Parameter(BaseParameter):
    class Meta(BaseParameter.Meta):
        db_table = 'wq_parameter'
        abstract = not (swapper.is_swapped('annotate', 'AnnotationType') == 'vera.Parameter')

class Result(BaseResult):
    class Meta(BaseResult.Meta):
        db_table = 'wq_result'
        abstract = not (swapper.is_swapped('annotate', 'Annotation') == 'vera.Result')
