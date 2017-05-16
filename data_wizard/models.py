from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from rest_framework.settings import import_from_string
from data_wizard import registry


LOADER_PATH = getattr(
    settings, 'DATA_WIZARD_LOADER', 'data_wizard.loaders.FileLoader'
)
Loader = import_from_string(LOADER_PATH, 'DATA_WIZARD_LOADER')


class Run(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    template = models.ForeignKey('self', null=True, blank=True)
    record_count = models.IntegerField(null=True, blank=True)
    loader = models.CharField(max_length=255, default=LOADER_PATH)
    serializer = models.CharField(max_length=255, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return "Run for %s" % self.content_object

    def save(self, *args, **kwargs):
        is_new = not self.id
        super(Run, self).save(*args, **kwargs)
        if is_new:
            self.add_event('created')

    def load_io(self):
        loader = Loader(self)
        return loader.load_io()

    def get_serializer(self):
        if self.serializer:
            return registry.get_serializer(self.serializer)
        else:
            raise Exception("No serializer specified!")

    def already_parsed(self):
        return self.range_set.count()

    def add_event(self, name):
        self.log.create(
            event=name
        )


class RunLog(models.Model):
    run = models.ForeignKey(Run, related_name='log')
    event = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s: %s at %s" % (self.run, self.event, self.date)

    class Meta:
        ordering = ('date',)


class Identifier(models.Model):
    serializer = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    field = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    attr_id = models.PositiveIntegerField(null=True, blank=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        if self.type == 'meta':
            return "%s -> %s" % (self.name, self.field)
        elif self.type == 'attribute':
            return "%s -> %s (attr=%s)" % (self.name, self.field, self.attr_id)
        elif self.type == 'instance':
            return "%s -> %s (%s)" % (self.name, self.value, self.field)
        else:
            return "%s: %s" % (self.type.title(), self.name)

    @property
    def type(self):
        if self.resolved:
            if self.attr_id is not None:
                return 'attribute'
            elif self.value is not None:
                return 'instance'
            elif self.field:
                return 'meta'
        else:
            if self.field:
                return 'unresolved'
            else:
                return 'unknown'


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

        return "{run} contains {type} '{ident}' at {row}, {col}{head}".format(
            run=self.run,
            type=self.get_type_display(),
            ident=self.identifier,
            row=row,
            col=col,
            head=header
        )

    class Meta:
        ordering = ('run_id', '-type', 'start_row', 'start_col', 'pk')


class Record(models.Model):
    run = models.ForeignKey(Run)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    row = models.PositiveIntegerField()
    success = models.BooleanField(default=True)
    fail_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.success:
            return "{run} imported '{obj}' at row {row}".format(
                run=self.run,
                obj=self.content_object,
                row=self.row,
            )
        else:
            return "{run} failed at row {row}: {fail_reason}".format(
                run=self.run,
                row=self.row,
                fail_reason=self.fail_reason,
            )

    class Meta:
        ordering = ('run_id', 'row')
