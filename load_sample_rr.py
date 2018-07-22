#!/usr/bin/env python
import os
import sys
import re
import django

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Usage: ./load_sample_rr.py <filename> <patient_id> \
               <admin username> [<type> [<name>]]')
        print('Type can be n (normal) or r (RR)')
        exit()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cardio.settings")
    django.setup()

    from apps.records.models import Point, Record, Channel
    from apps.patients.models import Patient
    from apps.users.models import User
    file_name = sys.argv[1]
    patient_id = sys.argv[2]
    user_id = sys.argv[3]
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        print('User {} not found'.format(
            user_id
        ))
        raise
    try:
        channel_type = sys.argv[4]
    except IndexError:
        channel_type = 'r'
    try:
        channel_name = sys.argv[5]
    except IndexError:
        channel_name = 'RR'

    if channel_type not in ('n', 'r'):
        print('Channel type must be n or r')
        exit()
    # f = open('samples/sanos/Sano_10002_01:00:00pm_Srr.dat')
    f = open(file_name)
    # f = open('samples/ecgsyn.dat')
    results = re.findall(r'(\d+)', f.read())
    # results = re.findall(r'(\d+\.?\d+)\s+(\d+\.?\d+)\s+(\d+)', f.read())
    patient = Patient.objects.get(pk=patient_id)
    record = Record.objects.create(
        patient=patient,
        taken_by=user
    )
    channel = Channel.objects.create(
        record=record, name=channel_name, type='r')

    length = len(results)
    _sum = 0

    print('Reading {} entries'.format(length))
    for index, result in enumerate(results):
        y = int(result)
        _sum += y
        Point.objects.create(
            channel=channel, x=index, y=y, y_accumulative=_sum)

    print('Finished reading %d entries' % length)
