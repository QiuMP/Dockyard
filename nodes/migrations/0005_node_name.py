# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0004_auto_20170513_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='name',
            field=models.CharField(default='debian_1', max_length=100),
            preserve_default=False,
        ),
    ]
