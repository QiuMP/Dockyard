# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0002_auto_20170422_0019'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='ip',
            field=models.CharField(default='0.0.0.0', max_length=100),
            preserve_default=False,
        ),
    ]
