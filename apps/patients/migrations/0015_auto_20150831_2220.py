# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0014_auto_20150831_2208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='education',
            options={'verbose_name': 'nivel educativo', 'verbose_name_plural': 'niveles educativos'},
        ),
        migrations.AlterModelOptions(
            name='habit',
            options={'verbose_name': 'h\xe1bito', 'verbose_name_plural': 'h\xe1bitos'},
        ),
        migrations.AlterModelOptions(
            name='history',
            options={'verbose_name': 'historial', 'verbose_name_plural': 'historial'},
        ),
        migrations.AlterModelOptions(
            name='occupation',
            options={'verbose_name': 'ocupaci\xf3n', 'verbose_name_plural': 'ocupaciones'},
        ),
        migrations.AlterModelOptions(
            name='patient',
            options={'verbose_name': 'paciente'},
        ),
        migrations.AlterModelOptions(
            name='relationshiptype',
            options={'verbose_name': 'parentesco'},
        ),
        migrations.AlterModelOptions(
            name='ses',
            options={'verbose_name': 'estatus socioecon\xf3mico'},
        )
    ]
