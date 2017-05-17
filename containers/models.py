from django.db import models


class Container(models.Model):
    class Meta:
        permissions = (
            ("view_containers", "Can see container's list"),
            ("modify_containers", "Can add and change container"),
        )
