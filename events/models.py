from django.db import models


class Event(models.Model):
    TYPE_CHOICES = {
        ('N', 'Node'),
        ('S', 'Service'),
        ('C', 'Container'),
        ('I', 'Image'),
        ('A', 'Account'),
    }
    time = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)
    type = models.CharField(max_length=1,
                            choices=TYPE_CHOICES)
    operation = models.CharField(max_length=300)

    def __unicode__(self):
        return self.user + ' ' + self.operation
