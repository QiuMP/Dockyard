# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('user', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=1, choices=[(b'A', b'Account'), (b'S', b'Service'), (b'N', b'Node'), (b'C', b'Container'), (b'I', b'Image')])),
                ('operation', models.CharField(max_length=300)),
            ],
        ),
    ]
