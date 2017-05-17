# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'permissions': (('view_images', "Can see image's list"), ('modify_images', 'Can add and change image'))},
        ),
    ]
