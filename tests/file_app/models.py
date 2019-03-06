from django.db import models


class File(models.Model):
    file = models.FileField()

    def __str__(self):
        return self.file.name
