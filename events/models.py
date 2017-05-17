from django.db import models

from nodes.models import Node


class Event(models.Model):
    TYPE_CHOICES = {
        ('N', 'Node'),
        ('S', 'Service'),
        ('C', 'Container'),
        ('I', 'Image'),
        ('A', 'Account'),
    }
    time = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=30)
    node = models.ForeignKey(Node, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=1,
                            choices=TYPE_CHOICES)
    operation = models.CharField(max_length=300)

    def __unicode__(self):
        return self.user + ' ' + self.operation

    class Meta:
        permissions = (
            ("view_events", "Can see event's list"),
            ("modify_events", "Can add and change event"),
        )
