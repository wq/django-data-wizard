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
    @property
    def valid_events(self):
        events = self.event_set.filter(
            report__status__is_valid=True
        ).values_list('pk', flat=True)
        # FIXME: events may be duplicated
        return self.event_set.filter(pk__in=events)

    class Meta:
        abstract = True


class BaseEvent(models.NaturalKeyModel):
    site = models.ForeignKey(MODELS['Site'])

    @property
    def valid_reports(self):
        return self.report_set.filter(status__is_valid=True).order_by(
            *VALID_REPORT_ORDER
        )

    @property
    def vals(self):
        return OrderedDict([
            (a.type.natural_key()[0], a.value)
            for a in self.annotations
        ])

    # Valid annotations for this event
    @property
    def annotations(self):
        Annotation = swapper.load_model('annotate', 'Annotation')
        AnnotationType = swapper.load_model('annotate', 'AnnotationType')
        # ORDER BY annotation type (parameter), then valid report order
        order = (nest_ordering('type', AnnotationType._meta.ordering)
                 + ['type__id']
                 + nest_ordering('report', VALID_REPORT_ORDER))
        # DISTINCT ON annotation types, collapsing multiple reports into one
        distinct = (nest_ordering('type', AnnotationType._meta.ordering, True)
                    + ['type__id'])
        annots = Annotation.objects.filter(report__in=self.valid_reports)
        if issubclass(Annotation, BaseResult):
            annots = annots.filter(empty=False)
        return annots.order_by(*order).distinct(*distinct)

    @property
    def is_valid(self):
        return self.valid_reports.count() > 0

    class Meta:
        abstract = True


class ReportManager(models.RelatedModelManager):
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


class BaseReport(models.AnnotatedModel, models.RelatedModel):
    event = models.ForeignKey(MODELS['Event'])
    entered = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.ForeignKey(MODELS['ReportStatus'], null=True, blank=True)

    @property
    def is_valid(self):
        return self.status and self.status.is_valid

    objects = ReportManager()
    valid_objects = ValidReportManager()

    def __unicode__(self):
        return "%s according to %s" % (self.event, self.user)

    class Meta:
        abstract = True
        ordering = VALID_REPORT_ORDER


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
        ordering = ('name',)


class BaseResult(models.BaseAnnotation):
    value_numeric = models.FloatField(null=True, blank=True)
    value_text = models.TextField(null=True, blank=True)
    empty = models.BooleanField(default=False, db_index=True)

    def is_empty(self, value):
        if value is None:
            return True
        if isinstance(value, basestring) and len(value.strip()) == 0:
            return True
        return False

    @property
    def value(self):
        if self.type.is_numeric:
            return self.value_numeric
        return self.value_text

    @value.setter
    def value(self, val):
        self.empty = self.is_empty(val)
        if self.type.is_numeric:
            if self.empty:
                self.value_numeric = None
            else:
                self.value_numeric = val
        else:
            self.value_text = val

    class Meta:
        abstract = True
        ordering = ('type',)
        index_together = [
            ('type', 'object_id', 'empty'),
        ]


# Default implementation of the above classes, can be swapped
class Site(BaseSite):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return "%s, %s" % (round(self.latitude, 3), round(self.longitude, 3))

    class Meta(BaseSite.Meta):
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


# These will be inactive unless they are explicitly swapped for annotate's
# equivalents
class Parameter(BaseParameter):
    class Meta(BaseParameter.Meta):
        db_table = 'wq_parameter'
        abstract = not (
            swapper.is_swapped('annotate', 'AnnotationType')
            == 'vera.Parameter'
        )


class Result(BaseResult):
    class Meta(BaseResult.Meta):
        db_table = 'wq_result'
        abstract = not (
            swapper.is_swapped('annotate', 'Annotation') == 'vera.Result'
        )


def nest_ordering(prefix, ordering, ignore_reverse=False):
    nest_order = []
    for field in ordering:
        reverse = ''
        if field.startswith('-'):
            field = field[1:]
            if not ignore_reverse:
                reverse = '-'
        nest_order.append(reverse + prefix + '__' + field)
    return nest_order
