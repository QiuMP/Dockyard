from django.db import models


class Service(models.Model):
    class Meta:
        permissions = (
            ("view_services", "Can see service's list"),
            ("modify_services", "Can add and change service"),
        )
