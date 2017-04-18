# -*- coding: utf-8 -*-

from django.db import models

# class Image(models.Model):
#     image_id = models.CharField(max_length=96, null=True, blank=True)
#     created = models.DateTimeField(null=True)
#     virtual_size = models.BigIntegerField()

#     # history = models.ForeignKey(History, null=True)
#     # node = models.ForeignKey(Node, null=True)

#     def __unicode__(self):
#         img_id = self.image_id if self.image_id else 'unknown'
#         return img_id


# class Tag(models.Model):
#     """
#     保存镜像的标签，即镜像名
#     """
#     tag = models.CharField(max_length=96)
#     image = models.ForeignKey(Image)
