from django.db import models


class SimpleModel(models.Model):
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('blue', 'Blue'),
    ]

    date = models.DateField()
    color = models.CharField(
        max_length=5, choices=COLOR_CHOICES, verbose_name="Color Choice"
    )
    notes = models.TextField()

    def __str__(self):
        return "%s: %s (%s)" % (
            self.date,
            self.color,
            self.notes,
        )


class Type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FKModel(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    notes = models.TextField()

    def __str__(self):
        return "%s (%s)" % (
            self.type,
            self.notes,
        )
