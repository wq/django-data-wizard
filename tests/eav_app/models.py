from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "entities"


class Attribute(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Value(models.Model):
    entity = models.ForeignKey(
        Entity, related_name='values', on_delete=models.PROTECT
    )
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)
    value = models.CharField(max_length=50)
    units = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return "%s for %s: %s%s" % (
            self.attribute,
            self.entity,
            self.value,
            " " + self.units if self.units else "",
        )
