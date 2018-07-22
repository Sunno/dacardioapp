# coding=utf-8
from datetime import timedelta

from apps.patients.models import OrderManager
from django.db import models
from django.db.models.aggregates import Avg, StdDev, Sum
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils import six
from django.utils.six.moves import xrange
from apps.records.helpers.points import get_max_pow2, get_pow2
import numpy
import math


# Create your models here.
@six.python_2_unicode_compatible
class Record(models.Model):
    patient = models.ForeignKey('patients.Patient',
                                verbose_name=_('paciente'),
                                related_name='records')
    taken_by = models.ForeignKey('users.User',
                                 verbose_name=_('registrado por'),
                                 related_name='records_loaded')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_(u'fecha de creación'))
    modified = models.DateTimeField(auto_now=True,
                                    verbose_name=_(u'fecha de modificación'))

    def __str__(self):
        return u'%s (%s)' % (self.patient.full_name, self.created.isoformat())

    class Meta:
        verbose_name = _('registro')


@six.python_2_unicode_compatible
class Channel(models.Model):
    CHANNEL_TYPES = (
        ('n', _('Normal')),
        ('i', _('Integrada')),
        ('c', _(u'Cuadrática')),
        ('o', _('Original')),
        ('d', _('Derivada')),
        ('f', _('Filtrada')),
        ('r', _('RR'))
    )

    record = models.ForeignKey(Record,
                               verbose_name=_('registro'),
                               related_name='channels')
    type = models.CharField(max_length=2,
                            default='n',
                            choices=CHANNEL_TYPES,
                            verbose_name=_('tipo'))
    name = models.CharField(max_length=50,
                            blank=True,
                            default='',
                            verbose_name=_('nombre'))
    description = models.TextField(blank=True,
                                   default='',
                                   verbose_name=_(u'descripción'))
    start_date = models.DateTimeField(default=timezone.now,
                                      blank=True,
                                      verbose_name=_('Fecha de inicio'))
    sampling_rate = models.IntegerField(default=500,
                                        verbose_name=_('Tasa de muestreo'))

    @property
    def end_date(self):
        milliseconds = self.duration
        return (self.start_date + timedelta(milliseconds=milliseconds)) \
            if self.start_date else None

    @property
    def duration(self):
        if self.is_time:
            return self.points.all().aggregate(sum=Sum('y'))['sum']
        return self.points.all().count() * self.sampling_rate

    @property
    def is_time(self):
        """
        Says if Y represents time or not
        :return: boolean
        """
        return self.type == 'r'

    @property
    def duration_str(self):
        return str(timedelta(milliseconds=self.duration))[:-4]

    class Meta:
        verbose_name = _('canal')
        verbose_name_plural = _('canales')

    def __str__(self):
        return 'Record: %s - %s - %s - Start: %s' % (str(self.record),
                                                     self.get_type_display(),
                                                     self.name,
                                                     self.start_date.
                                                     isoformat()
                                                     if self.start_date else '')

    def get_media_points(self, initial_time, final_time, interval):
        y = []
        while initial_time < final_time:
            if self.is_time:
                avg = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval)\
                    .order_by('x').aggregate(average=Avg('y'))['average']
            else:
                avg = self.points.filter(
                    x___gte=initial_time,
                    x__lte=initial_time+interval).order_by('x')\
                    .aggregate(average=Avg('y'))['average']
            if avg is not None:
                y.append(avg)

            initial_time += interval
        return range(1, len(y) + 1), y

    def get_standard_deviation_points(self, initial_time, final_time, interval):
        y = []
        while initial_time < final_time:
            if self.is_time:
                std_dev = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval)\
                    .order_by('x').aggregate(std_dev=StdDev('y'))
            else:
                std_dev = self.points.filter(
                    x__gte=initial_time,
                    x__lte=initial_time+interval)\
                    .order_by('x').aggregate(std_dev=StdDev('y'))

            if std_dev['std_dev'] is not None:
                y.append(std_dev['std_dev'])
            else:
                break
            initial_time += interval
        return range(1, len(y) + 1), y

    def get_standard_deviation(self, initial_time, final_time):

        if self.is_time:
            return self.points.filter(
                y_accumulative__gte=initial_time,
                y_accumulative__lte=final_time).order_by('x')\
                .aggregate(std_dev=StdDev('y'))['std_dev']

        return \
            self.points.filter(
                x__gte=initial_time,
                x__lte=final_time).order_by('x')\
            .aggregate(std_dev=StdDev('y'))['std_dev']

    def get_media(self, initial_time, final_time):
        if self.is_time:
            return \
                self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=final_time)\
                .order_by('x').aggregate(avg=Avg('y'))['avg']

        return \
            self.points.filter(
                x__gte=initial_time,
                x__lte=final_time).order_by('x').aggregate(avg=Avg('y'))['avg']

    def get_return_map(self, initial_time, final_time):
        if self.is_time:
            points = [point.y for point in
                      self.points.filter(
                          y_accumulative__gte=initial_time,
                          y_accumulative__lte=final_time).order_by('x')]
        else:
            points = [point.y for point in self.points.filter(
                x__gte=initial_time, x__lte=final_time).order_by('x')]
        x = []
        y = []

        for index in xrange(len(points) - 1):
            try:
                y.append(points[index+1])
                x.append(points[index])
            except IndexError:
                break
        return x, y

    def get_PNN50(self, initial_time, final_time):
        if self.is_time:
            points = self.points.filter(
                y_accumulative__gte=initial_time,
                y_accumulative__lte=final_time
            ).order_by('x')
        else:
            points = self.points.filter(
                x__gte=initial_time / self.sampling_rate,
                x__lte=final_time / self.sampling_rate
            ).order_by('x')

        length = points.count()
        if length == 0:
            return None

        last_value = points[0].y
        counter = 0
        for point in points:
            if abs(last_value - point.y) > 50:
                counter += 1
            last_value = point.y
        return (float(counter) / float(length - 1)) * 100

    def get_PNN50_points(self, initial_time, final_time, interval):
        y = []
        while initial_time < final_time:
            pnn50 = self.get_PNN50(initial_time, initial_time + interval)
            y.append(pnn50)
            initial_time += interval
        return range(1, len(y) + 1), y

    def get_SDNNindex(self, initial_time, final_time, interval):
        sum = 0
        n = 0
        while initial_time < final_time:
            if self.is_time:
                std_dev = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval)\
                    .order_by('x').aggregate(std_dev=StdDev('y'))['std_dev']
            else:
                std_dev = self.points.filter(
                    x__gte=initial_time,
                    x__lte=initial_time+interval)\
                    .order_by('x').aggregate(std_dev=StdDev('y'))['std_dev']
            sum += (std_dev if std_dev is not None else 0)
            n += 1
            initial_time += interval
        return sum / n if n > 0 else 0

    def get_SDANN(self, initial_time, final_time, interval):
        y = []
        while initial_time < final_time:
            if self.is_time:
                avg = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval
                ).order_by('x').aggregate(average=Avg('y'))['average']
            else:
                avg = self.points.filter(
                        y___gte=initial_time,
                        x__lte=initial_time+interval) \
                    .order_by('x').aggregate(average=Avg('y'))['average']

            y.append(avg if avg is not None else 0)
            initial_time += interval
        return numpy.std(y)

    def get_SDSD(self, initial_time, final_time, interval):
        y = []
        if not self.is_time:
            interval = interval / self.sampling_rate
        while initial_time < final_time:
            if self.is_time:
                points = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval)

            else:
                points = self.points.filter(
                    y___gte=initial_time,
                    x__lte=initial_time+interval).order_by('x')

            initial_time += interval
            differences = []
            if points.exists():
                aux = points[0]
                for point in points[1:]:
                    differences.append((aux.y - point.y) ** 2)
                    aux = point
                y.append(numpy.mean(differences) ** 0.5)
        return xrange(1, len(y) + 1), y  # TODO check this

    def get_fft(self, initial_time, final_time, interval):
        windows = []
        while initial_time < final_time:
            if self.is_time:
                points = self.points.filter(
                    y_accumulative__gte=initial_time,
                    y_accumulative__lte=initial_time + interval)

            else:
                points = self.points.filter(
                    y___gte=initial_time,
                    x__lte=initial_time+interval).order_by('x')
            if points.count() > 0:
                windows.append([p.y for p in points])
            initial_time += interval

        # determine which pow2 is the max we can use
        max_pow = get_max_pow2(windows)
        pow2 = 2**max_pow
        fft_sets = [
            numpy.fft.fft(p[:pow2]).real
            for p in windows]

        # indexes = [float(i)/(pow2) for i in xrange(pow2/2)]
        indexes = numpy.fft.fftfreq(pow2)[:int(pow2/2)]
        fft_sets = [[(math.sqrt((pts[i]**2 + pts[pow2-i-1]**2)/2.0)/(pow2/2.0),
                      ((pts[i]**2 + pts[pow2-i-1]**2) / 2.0))
                     for i in xrange(int(pow2/2))]
                    for pts in fft_sets]

        '''vlf = [
            sum([point for point in pts if point <= 0.038])
            for pts in ftt_sets
        ]'''
        lf = [
            (sum(
                [point[0] for i, point in enumerate(pts)
                 if indexes[i] > 0.038 and indexes[i] <= 0.16]
            ),
             sum(
                [point[1] for i, point in enumerate(pts)
                 if indexes[i] > 0.038 and indexes[i] <= 0.16]
            ))
            for pts in fft_sets
        ]
        hf = [
            (sum(
                [point[0] for i, point in enumerate(pts)
                 if indexes[i] > 0.16 and indexes[i] <= 0.5]
            ),
             sum(
                [point[1] for i, point in enumerate(pts)
                 if indexes[i] > 0.16 and indexes[i] <= 0.5]
            ))
            for pts in fft_sets
        ]
        len_sets = len(fft_sets)
        power = [lf[i][1] + hf[i][1] for i in xrange(len_sets)]

        relation = [lf[i][0] / hf[i][0] for i in xrange(len_sets)]

        # Normalizing
        sum_lf_hf = [lf[i][0] + hf[i][0] for i in xrange(len_sets)]
        lf = [a[0]/b for a, b in zip(lf, sum_lf_hf)]
        hf = [a[0]/b for a, b in zip(hf, sum_lf_hf)]
        return lf, hf, power, relation, xrange(1, len(fft_sets) + 1)

    def get_total_fft(self):
        pow2 = get_pow2(self.points.all().count())
        pow2 = 2**pow2
        points = [point.y for point in self.points.all().order_by('x')]
        fft = numpy.fft.fft(points[:pow2], norm='ortho').real[:pow2/2]
        indexes = [float(i)/(pow2) for i in xrange(pow2/2)]

        lf = sum([point for i, point in enumerate(fft)
                 if indexes[i] > 0.038 and indexes[i] <= 0.16]
                 )
        hf = sum([point for i, point in enumerate(fft)
                 if indexes[i] > 0.16 and indexes[i] <= 0.5]
                 )
        power = lf + hf

        relation = lf/hf

        return lf, hf, power, relation

    @property
    def SDNN(self):
        return self.points.all().aggregate(std_dev=StdDev('y'))['std_dev']

    @property
    def average(self):
        return self.points.all().aggregate(avg=Avg('y'))['avg']

    def fill_accumulatives(self):
        """
        Fills all Point.y_accumulative
        :return: NoneType
        """
        sum = 0
        for point in self.points.all().order_by('x'):
            sum += point.y
            point.y_accumulative = sum
            point.save()


@six.python_2_unicode_compatible
class Point(models.Model):
    WAVES_TYPES = (
        (None, 'None'),
        ('p', 'p'),
        ('q', 'q'),
        ('r', 'r'),
        ('s', 's'),
        ('u', 'u')
    )

    channel = models.ForeignKey(Channel,
                                verbose_name=_('canal'), related_name='points')
    x = models.FloatField(db_index=True)
    y = models.FloatField()
    y_accumulative = models.FloatField(default=0,
                                       verbose_name=_('Y acumulativo'),
                                       help_text=_(
                                           'La sumatoria de todos los valores \
                                           "Y" hasta el actual, se calcula con \
                                           Channel.fill_accumulatives'))
    wave = models.CharField(max_length=1,
                            choices=WAVES_TYPES,
                            null=True,
                            blank=True, verbose_name=_('onda detectada'))
    flagged = models.BooleanField(default=False, verbose_name=_('marca'))

    def __str__(self):
        return u'%s - %s - %s' % (str(self.channel), self.x, self.y)

    class Meta:
        verbose_name = _('punto')


@six.python_2_unicode_compatible
class Anomaly(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_('orden'))

    objects = OrderManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'anomalía')


@six.python_2_unicode_compatible
class Annotation(models.Model):
    point = models.ForeignKey('records.Point', verbose_name=_('punto'))
    annotation_type = models.CharField(max_length=45, verbose_name=_('tipo'))
    annotation = models.TextField()
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_(u'fecha de creación'))
    created_by = models.ForeignKey('users.User', verbose_name=_('creado por'))
    anomaly = models.ForeignKey('records.Anomaly',
                                null=True,
                                blank=True,
                                verbose_name=_(u'anomalía'))

    def __str__(self):
        return u'(%s) - %s - %s' % (
            str(self.point),
            self.created_by.full_name,
            self.created.isoformat())

    class Meta:
        verbose_name = _(u'anotación')
        verbose_name_plural = _('anotaciones')
