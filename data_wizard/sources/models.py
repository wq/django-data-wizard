from django.db import models


class FileSource(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to='datawizard/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.file.name


class URLSource(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.url
