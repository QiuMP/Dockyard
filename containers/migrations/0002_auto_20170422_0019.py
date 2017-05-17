# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='container',
            options={'permissions': (('view_containers', "Can see container's list"), ('modify_containers', 'Can add and change container'))},
        ),
    ]
