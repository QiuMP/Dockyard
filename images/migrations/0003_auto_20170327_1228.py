# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_auto_20170324_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='image',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
