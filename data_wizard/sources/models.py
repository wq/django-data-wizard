from django.db import models
from django.conf import settings
import os


class FileSource(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to="datawizard/")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or os.path.basename(self.file.name)


class URLSource(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.url
