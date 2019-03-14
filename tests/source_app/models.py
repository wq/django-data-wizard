from django.db import models


class CustomSource(models.Model):
    json_data = models.TextField()
