# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='node',
            field=models.ForeignKey(to='nodes.Node', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='user',
            field=models.CharField(max_length=30),
        ),
    ]
