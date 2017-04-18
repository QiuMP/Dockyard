# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='names',
        ),
        migrations.AddField(
            model_name='tag',
            name='image',
            field=models.ForeignKey(default=123, to='images.Image'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='image',
            name='virtual_size',
            field=models.BigIntegerField(default=123),
            preserve_default=False,
        ),
    ]
