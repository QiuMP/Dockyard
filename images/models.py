# -*- coding: utf-8 -*-

from django.db import models


class Image(models.Model):
    class Meta:
        permissions = (
            ("view_images", "Can see image's list"),
            ("modify_images", "Can add and change image"),
        )
