from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=50, unique=True)
    ip = models.CharField(max_length=20)
    port = models.IntegerField(default=5000)

    def get_address(self):
        return "tcp://" + self.ip + ":" + str(self.port)

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ("view_nodes", "Can see node's list"),
            ("modify_nodes", "Can add and change node"),
        )
