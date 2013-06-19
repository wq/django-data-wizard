from wq.db.patterns import models
from wq.db.patterns.base import swapper

class File(swapper.load_model('files', 'File')):
    def set_template(self, template_id):
        template = File.objects.get(pk__in=template_id)
        template.create_relationship(self, 'Template For', 'Template')

    class Meta:
        proxy = True

class MetaColumn(models.IdentifiedRelatedModel):
    DATA_TYPES = (
        ('event', 'Event Metadata'),
        ('report', 'Report Metadata'),
        ('parameter', 'Parameter Metadata'),
        ('result', 'Result Data/Metadata'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=DATA_TYPES)

    def __unicode__(self):
        name = super(MetaColumn, self).__unicode__()
        return "%s (%s)" % (name, self.get_type_display())

    class Meta:
        db_table = 'wq_metacolumn'
        app_label = 'vera'

class UnknownItem(models.IdentifiedRelatedModel):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
        
    class Meta:
        db_table = 'wq_unknownitem'
        app_label = 'vera'

class Range(models.Model):
    RANGE_TYPES = (
        ('head', 'Column header / label'),
        ('value', 'Global Value'),
        ('list', 'Data series'),
    )
    relationship = models.ForeignKey(models.Relationship)
    type = models.CharField(max_length=10, choices=RANGE_TYPES)
    start_row    = models.IntegerField()
    end_row      = models.IntegerField(null=True, blank=True)
    start_column = models.IntegerField()
    end_column   = models.IntegerField()

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
        app_label = 'vera'
