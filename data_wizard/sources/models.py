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
    file = models.FileField(upload_to="datawizard/")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Name (Optional)")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    class Meta:
        verbose_name = "File for Import"
        verbose_name_plural = "Import via File"


class URLSource(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    url = models.URLField()
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Name (Optional)")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.url

    class Meta:
        verbose_name = "URL for Import"
        verbose_name_plural = "Import via URL"
