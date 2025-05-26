# This file is part of the Django application for managing stores.
from django.db import models

class request_hist(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=255)
    budget = models.IntegerField()
    theme = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.location