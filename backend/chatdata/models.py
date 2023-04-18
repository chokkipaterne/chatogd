from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
#CKAN, ODS
class SystemPortal(models.Model):
    name = models.CharField(max_length=255)
    more_details = JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'SystemPortal'
        verbose_name_plural = 'SystemPortals'
        ordering = ['name']

# Create your models here.
class PlatformPortal(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    sequence = models.IntegerField(default=1)
    system = models.ForeignKey(SystemPortal,
        related_name="platformportals", on_delete=models.SET_NULL, null=True, blank=True)
    more_details = JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'PlatformPortal'
        verbose_name_plural = 'PlatformPortals'
        ordering = ['name']

#Model to store the different open data portals
class DataPortal(models.Model):
    identifier = models.CharField(max_length=255)
    more_details = JSONField(blank=True, default=dict)
    platform = models.ForeignKey(PlatformPortal,
        related_name="dataportals", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.identifier

    class Meta:
        verbose_name = 'DataPortal'
        verbose_name_plural = 'DataPortals'
        ordering = ['identifier']
