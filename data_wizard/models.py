from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from rest_framework.settings import import_from_string


LOADER_PATH = getattr(
    settings, 'DATA_WIZARD_LOADER', 'data_wizard.loaders.FileLoader'
)
Loader = import_from_string(LOADER_PATH, 'DATA_WIZARD_LOADER')


class Run(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    template = models.ForeignKey('self', null=True, blank=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return "Run for %s" % self.content_object

    def load_io(self):
        loader = Loader(self)
        return loader.load_io()

    def already_parsed(self):
        return self.range_set.count()


class RunLog(models.Model):
    run = models.ForeignKey(Run)
    event = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)


class Identifier(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)

    field = models.CharField(max_length=255, null=True, blank=True)

    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    resolved = models.BooleanField(default=False)
    meta = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.type == 'instance':
            return "%s: %s" % (self.content_type, self.content_object)
        else:
            return "%s: %s" % (self.type.title(), self.name)

    @property
    def type(self):
        if self.resolved:
            if self.object_id:
                return 'instance'
            elif self.field:
                return 'meta'
        else:
            if self.content_type:
                return 'unresolved'
            else:
                return 'unknown'

    def save(self, *args, **kwargs):
        if self.object_id or self.field:
            self.resolved = True
        super(Identifier, self).save(*args, **kwargs)


class Range(models.Model):
    RANGE_TYPES = (
        ('list', 'Data Column'),
        ('value', 'Header metadata'),
        ('data', 'Cell value'),
    )
    run = models.ForeignKey(Run)
    identifier = models.ForeignKey(Identifier)
    type = models.CharField(max_length=10, choices=RANGE_TYPES)

    header_col = models.IntegerField()
    start_col = models.IntegerField()
    end_col = models.IntegerField(null=True, blank=True)

    header_row = models.IntegerField()
    start_row = models.IntegerField()
    end_row = models.IntegerField(null=True, blank=True)

    count = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.header_col is None:
            self.header_col = self.start_col
        if self.header_row is None:
            self.header_row = self.start_row
        super(Range, self).save()

    def __str__(self):
        if self.start_row == self.end_row:
            row = "Row %s" % self.start_row
        elif self.end_row is not None:
            row = "Rows %s-%s" % (self.start_row, self.end_row)
        else:
            row = "Row %s onward" % (self.start_row,)

        if self.start_col == self.end_col:
            col = "Column %s" % self.start_col
        elif self.end_col is not None:
            col = "Column %s-%s" % (self.start_col, self.end_col)
        else:
            row = "Column %s onward" % (self.start_col,)
        header = ""
        if self.type == "list" and self.header_row != self.start_row - 1:
            header = " (header starts in Row %s)" % self.header_row
        elif self.type == "value" and self.header_col != self.start_col - 1:
            header = " (header starts in Column %s)" % self.header_col

        return "%s contains %s at %s, %s%s" % (
            self.run, self.identifier, row, col, header
        )


class Record(models.Model):
    run = models.ForeignKey(Run)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    row = models.PositiveIntegerField()
    success = models.BooleanField(default=True)
    fail_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.reason
