from wq.db.patterns import models


class MetaColumn(models.IdentifiedRelatedModel):
    DATA_TYPES = (
        ('site', 'Site Metadata'),
        ('event', 'Event Metadata'),
        ('report', 'Report Metadata'),
        ('parameter', 'Parameter Metadata'),
        ('result', 'Result Data/Metadata'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=DATA_TYPES, blank=True)

    def __unicode__(self):
        name = super(MetaColumn, self).__unicode__()
        return "%s (%s)" % (name, self.get_type_display())

    class Meta:
        db_table = 'wq_metacolumn'


class UnknownItem(models.IdentifiedRelatedModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'wq_unknownitem'


class SkippedRecord(models.Model):
    reason = models.TextField()

    def __unicode__(self):
        return self.reason

    class Meta:
        db_table = 'wq_skippedrecord'


class Range(models.Model):
    RANGE_TYPES = (
        ('head', 'Column header / label'),
        ('value', 'Global Value'),
        ('list', 'Data series'),
        ('row', 'Individual Record'),
    )
    relationship = models.ForeignKey(models.Relationship)
    type = models.CharField(max_length=10, choices=RANGE_TYPES)
    start_row = models.IntegerField()
    end_row = models.IntegerField(null=True, blank=True)
    start_column = models.IntegerField()
    end_column = models.IntegerField()

    def __unicode__(self):
        if self.start_row == self.end_row:
            row = "Row %s" % self.start_row
        else:
            if self.end_row is not None:
                row = "Rows %s-%s" % (self.start_row, self.end_row)
            else:
                row = "Row %s onward" % (self.start_row,)

        if self.start_column == self.end_column:
            column = "Column %s" % self.start_column
        else:
            column = "Column %s-%s" % (self.start_column, self.end_column)

        return "%s at %s, %s" % (self.relationship, row, column)

    class Meta:
        db_table = 'wq_range'


class IoModel(models.RelatedModel):
    def load_io(self, **options):
        raise NotImplementedError()

    def already_parsed(self):
        return self.relationships.filter(
            type__name='Contains Column',
            range__type='list'
        ).exists()

    def get_id_choices(self, model):
        return model.objects.all()

    class Meta:
        abstract = True
