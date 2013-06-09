from wq.db.patterns import models

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
        return "%s (%s)" % (self.name, self.get_type_display())

    class Meta:
        db_table = 'wq_metacolumn'

class UnknownItem(models.IdentifiedRelatedModel):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
        
    class Meta:
        db_table = 'wq_unknownitem'

class Range(models.Model):
    relationship = models.ForeignKey(models.Relationship)
    start_row    = models.IntegerField()
    end_row      = models.IntegerField()
    start_column = models.IntegerField()
    end_column   = models.IntegerField()

    def __unicode__(self):
        if self.start_row == self.end_row:
            row = "Row %s" % self.start_row
        else:
            row = "Rows %s-%s" % (self.start_row, self.end_row)

        if self.start_column == self.end_column:
            column = "Column %s" % self.start_column
        else:
            column = "Column %s-%s" % (self.start_column, self.end_column)

        return "%s at %s, %s" % (self.relationship, row, column)
    
    class Meta:
        db_table = 'wq_range'
