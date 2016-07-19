from django.db import models

from apps.dvobjects.models import DvObject

class Datafile(models.Model):
    id = models.OneToOneField(DvObject, db_column='id', primary_key=True)

    name = models.CharField(max_length=255, blank=True, null=True)

    contenttype = models.CharField(max_length=255)

    filesystemname = models.CharField(max_length=255)

    filesize = models.BigIntegerField(blank=True, null=True)

    ingeststatus = models.CharField(max_length=1, blank=True, null=True)

    md5 = models.CharField(max_length=255)

    restricted = models.BooleanField()

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        managed = False
        db_table = 'datafile'
