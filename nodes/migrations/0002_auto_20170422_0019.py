# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='node',
            options={'permissions': (('view_nodes', "Can see node's list"), ('modify_nodes', 'Can add and change node'))},
        ),
    ]
