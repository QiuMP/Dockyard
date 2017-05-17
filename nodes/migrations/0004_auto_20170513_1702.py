# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0003_node_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='port',
            field=models.IntegerField(default=5000),
        ),
        migrations.AlterField(
            model_name='node',
            name='ip',
            field=models.CharField(max_length=50),
        ),
    ]
