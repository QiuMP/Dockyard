# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0005_node_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
