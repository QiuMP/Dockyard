# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0006_auto_20170513_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='ip',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='node',
            name='name',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
