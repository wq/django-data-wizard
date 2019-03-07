from django.db import models
from natural_keys import NaturalKeyModel


class Place(NaturalKeyModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)


class Event(NaturalKeyModel):
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    date = models.DateField()

    def __str__(self):
        return "%s on %s" % (self.place, self.date)

    class Meta:
        unique_together = (('place', 'date'),)


class Note(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    note = models.TextField()
    status = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return "%s: %s" % (self.event, self.note)
