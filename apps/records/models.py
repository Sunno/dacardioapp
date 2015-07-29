from django.db import models

# Create your models here.
class Record(models.Model):
    patient = models.ForeignKey('patients.Patient')
    taken_by = models.ForeignKey('users.User')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Point(models.Model):
    WAVES_TYPES = (
        (None, 'None'),
        ('p', 'p'),
        ('q', 'q'),
        ('r', 'r'),
        ('s', 's'),
        ('u', 'u')
    )

    record = models.ForeignKey('records.Record')
    x = models.FloatField()
    y = models.FloatField()
    wave = models.CharField(max_length=1, choices=WAVES_TYPES, null=True, blank=True)
    flagged = models.BooleanField(default=False)


class Anomaly(models.Model):
    name = models.CharField(max_length=256)


class Annotation(models.Model):
    point = models.ForeignKey('records.Point')
    annotation_type = models.CharField(max_length=45)
    annotation = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User')
    anomaly = models.ForeignKey('records.Anomaly', null=True, blank=True)

