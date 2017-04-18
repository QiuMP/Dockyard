# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_id', models.CharField(max_length=96, null=True, blank=True)),
                ('created', models.DateTimeField(null=True)),
                ('virtual_size', models.BigIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=96)),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='names',
            field=models.ForeignKey(to='images.Tag'),
        ),
    ]
