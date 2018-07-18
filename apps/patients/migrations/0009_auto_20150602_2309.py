# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0008_auto_20150602_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='street',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='street_2',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
