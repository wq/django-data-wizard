from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.urls import reverse
from . import registry
from .settings import import_setting, get_setting


class Run(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    record_count = models.IntegerField(null=True, blank=True)
    loader = models.CharField(max_length=255, null=True, blank=True)
    serializer = models.CharField(max_length=255, null=True, blank=True)

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return str(self.content_object)

    def get_absolute_url(self):
        return reverse("data_wizard:run-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.loader:
            self.loader = registry.get_loader_name(type(self.content_object))

        if self.loader and not self.serializer:
            try:
                Loader = registry.get_loader(self.loader)
            except ImportError:
                pass
            else:
                self.serializer = Loader(self).get_serializer_name()

        is_new = not self.id
        super(Run, self).save(*args, **kwargs)
        if is_new:
            self.add_event("created")

    def load_iter(self):
        if not hasattr(self, "_iter_data"):
            Loader = registry.get_loader(self.loader)
            loader = Loader(self)
            self._iter_data = loader.load_iter()
        return self._iter_data

    def run_task(self, name, use_async=False, post=None):
        return self.backend.run(
            name,
            self.pk,
            use_async,
            post,
        )

    def run_all(self, tasks):
        return self.backend.run_all(self, tasks)

    def get_auto_import_tasks(self):
        if self.serializer:
            tasks = self.get_serializer_options().get("auto_import_tasks")
            if tasks:
                return tasks

        return get_setting("AUTO_IMPORT_TASKS")

    def send_progress(self, meta, state="PROGRESS"):
        self.backend.send_progress(self, meta, state)

    @property
    def backend(self):
        from . import backend as data_wizard_backend

        return data_wizard_backend

    @property
    def serializer_label(self):
        if self.serializer:
            return registry.get_serializer_name(self.serializer)

    serializer_label.fget.short_description = "serializer"

    def get_serializer(self):
        if self.serializer:
            return registry.get_serializer(self.serializer)
        else:
            raise Exception("No serializer specified!")

    def get_serializer_options(self):
        if self.serializer:
            return registry.get_serializer_options(self.serializer)
        else:
            raise Exception("No serializer specified!")

    def get_idmap(self):
        idmap = self.get_serializer_options().get("idmap")
        if not idmap:
            idmap = import_setting("IDMAP")
        return idmap

    def already_parsed(self):
        return self.range_set.count()

    def add_event(self, name):
        self.log.create(event=name)

    @property
    def last_update(self):
        last = self.log.last()
        if last:
            return last.date

    class Meta:
        ordering = ("-pk",)
        verbose_name = "data wizard"
        verbose_name_plural = "data wizard"


class RunLog(models.Model):
    run = models.ForeignKey(Run, related_name="log", on_delete=models.CASCADE)
    event = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event

    class Meta:
        ordering = ("date",)


class Identifier(models.Model):
    serializer = models.CharField(max_length=255)
    name = models.CharField(
        max_length=255,
        verbose_name="spreadsheet value",
    )
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="mapped value",
    )
    field = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="serializer field",
    )
    attr_field = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="EAV attribute field",
    )
    attr_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="EAV attribute id",
    )
    resolved = models.BooleanField(default=False)

    def __str__(self):
        if self.mapping_label:
            return "{name} -> {mapping}".format(
                name=self.name, mapping=self.mapping_label
            )
        else:
            return "{type}: {name}".format(
                type=self.type_label, name=self.name
            )

    @property
    def type(self):
        if self.resolved:
            if self.attr_id is not None:
                return "attribute"
            elif self.value is not None:
                return "instance"
            elif self.field:
                return "meta"
        else:
            if self.field:
                return "unresolved"
            else:
                return "unknown"

    @property
    def type_label(self):
        if self.type == "attribute":
            return "EAV Column"
        elif self.type == "meta":
            return "Column/Header"
        elif self.type == "instance":
            return "FK Value"
        else:
            return self.type.title()

    type_label.fget.short_description = "Type"

    @property
    def mapping_label(self):
        if self.type == "meta":
            if self.field == "__ignore__":
                return "(ignored)"
            else:
                return self.field
        elif self.type == "attribute":
            if "[]" in self.field:
                prefix, field_name = self.field.split("[]")
                field_name = field_name.strip("[]")
            else:
                prefix = ""
                field_name = self.field
            if self.attr_field and "[]" in self.attr_field:
                attr_prefix, attr_field_name = self.attr_field.split("[]")
                # assert attr_prefix == prefix
                attr_field_name = attr_field_name.strip("[]")
            else:
                attr_field_name = "attr"
            return "{prefix}.{field} ({attr_field}={attr_id})".format(
                prefix=prefix,
                field=field_name,
                attr_field=attr_field_name,
                attr_id=self.attr_id,
            )
        elif self.type == "instance":
            return "{field}={value}".format(
                field=self.field,
                value=self.value,
            )

    mapping_label.fget.short_description = "Mapped To"

    @property
    def serializer_label(self):
        if self.serializer:
            return registry.get_serializer_name(self.serializer)

    serializer_label.fget.short_description = "Serializer"


class Range(models.Model):
    RANGE_TYPES = (
        ("list", "Data Column"),
        ("value", "Header metadata"),
        ("data", "Cell value"),
    )
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    identifier = models.ForeignKey(Identifier, on_delete=models.PROTECT)
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
            col = "Column %s onward" % (self.start_col,)
        header = ""
        if self.type == "list" and self.header_row != self.start_row - 1:
            header = " (header starts in Row %s)" % self.header_row
        elif self.type == "value" and self.header_col != self.start_col - 1:
            header = " (header starts in Column %s)" % self.header_col

        return "{type} '{ident}' at {row}, {col}{head}".format(
            type=self.get_type_display(),
            ident=self.identifier,
            row=row,
            col=col,
            head=header,
        )

    class Meta:
        ordering = ("run_id", "-type", "start_row", "start_col", "pk")


class Record(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.PROTECT
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    row = models.PositiveIntegerField()
    success = models.BooleanField(default=True)
    fail_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.success:
            return "Imported '{obj}' at row {row}".format(
                obj=self.content_object,
                row=self.row,
            )
        else:
            return "Failed at row {row}".format(
                row=self.row,
            )

    class Meta:
        ordering = ("run_id", "row")
