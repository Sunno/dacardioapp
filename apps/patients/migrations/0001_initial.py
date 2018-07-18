# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='FamilyRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('modified_field', models.CharField(max_length=32)),
                ('modified_by', models.ForeignKey(related_name='history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(max_length=256)),
                ('id_card_prefix', models.CharField(default=b'V', max_length=1, choices=[(b'V', b'V'), (b'J', b'J'), (b'G', b'G'), (b'E', b'E')])),
                ('id_card_number', models.CharField(unique=True, max_length=32)),
                ('birth_date', models.DateField()),
                ('gender', models.CharField(max_length=1, choices=[(b'M', 'Masculino'), (b'F', 'Femenino')])),
                ('dwelling', models.BooleanField(default=True)),
                ('street', models.TextField()),
                ('street_2', models.TextField()),
                ('education', models.ForeignKey(related_name='patients', to='patients.Education')),
                ('habits', models.ManyToManyField(related_name='patients', to='patients.Habit')),
                ('occupation', models.ForeignKey(related_name='patients', to='patients.Occupation')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('patient', models.ForeignKey(related_name='personal_record', to='patients.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Ses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='ses',
            field=models.ForeignKey(related_name='patients', verbose_name=b'Socioeconomic status', to='patients.Ses'),
        ),
        migrations.AddField(
            model_name='history',
            name='patient',
            field=models.ForeignKey(related_name='history', to='patients.Patient'),
        ),
        migrations.AddField(
            model_name='familyrecord',
            name='patient',
            field=models.ForeignKey(related_name='family_record', to='patients.Patient'),
        ),
        migrations.AddField(
            model_name='familyrecord',
            name='relationship_type',
            field=models.ForeignKey(related_name='family_record', to='patients.RelationshipType'),
        ),
    ]
