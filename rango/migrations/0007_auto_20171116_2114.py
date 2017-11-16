# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0006_auto_20171116_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='first_visit',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='last_visit',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
