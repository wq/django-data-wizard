from django.db import models


class CustomSource(models.Model):
    json_data = models.TextField()


class CustomWorkflow(models.Model):
    validated = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    finalized = models.BooleanField(default=False)
