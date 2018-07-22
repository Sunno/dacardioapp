# -*- coding: utf-8 -*-
import os
import uuid
import mimetypes
from django.utils import six
from django.db import models
from django.db.models.aggregates import Max, Min
from django.utils.translation import ugettext as _
from django.utils import timezone


# managers
class OrderManager(models.Manager):
    def get_queryset(self):
        return super(OrderManager, self).get_queryset().order_by('order')


class OrderNameManager(OrderManager):
    def get_queryset(self):
        return super(OrderNameManager, self).get_queryset().order_by('name')


# ################## Info models
@six.python_2_unicode_compatible
class Ses(models.Model):
    """
    Socioeconomic status
    """
    name = models.CharField(max_length=128, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('orden'))

    objects = OrderNameManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'estatus socioeconómico')


@six.python_2_unicode_compatible
class Education(models.Model):
    """
    Education level
    """
    name = models.CharField(max_length=128, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('orden'))

    objects = OrderManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'nivel educativo')
        verbose_name_plural = _(u'niveles educativos')


@six.python_2_unicode_compatible
class Occupation(models.Model):
    """
    What the patient does
    """
    name = models.CharField(max_length=128, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('orden'))

    objects = OrderManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'ocupación')
        verbose_name_plural = _('ocupaciones')


@six.python_2_unicode_compatible
class Habit(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('orden'))

    objects = OrderManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'hábito')
        verbose_name_plural = _(u'hábitos')


@six.python_2_unicode_compatible
class RelationshipType(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('nombre'))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('orden'))

    objects = OrderManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('parentesco')


def get_upload_path(instance, filename):
    return os.path.join(
        'patients', str(uuid.uuid4()) +
        ('.' + filename.split('.')[-1] if filename not in (None, '') else
         mimetypes.guess_extension(instance.image.file.content_type)))


# ################## Patient data models
@six.python_2_unicode_compatible
class Patient(models.Model):
    """
    The patient
    """
    # Constants
    ID_CARD_PREFIXES = (
        ('V', 'V'),
        ('J', 'J'),
        ('G', 'G'),
        ('E', 'E')
    )

    GENDERS = (
        ('M', _('Masculino')),
        ('F', _('Femenino')),
    )

    MARITAL_STATUS = (
        ('s', _('Soltero')),
        ('m', _('Casado')),
        ('w', _('Viudo')),
        ('d', _('Divorciado')),
    )

    ORDERING = (
        'name',
        'id',
        'age',
        'creation',
        'modification',
        'id_card',
        'gender'
    )

    # Fields
    active = models.BooleanField(default=True)
    chart_number = models.CharField(
        max_length=50,
        verbose_name=_(u'número de historia'), null=True, blank=True)
    first_name = models.CharField(max_length=256, verbose_name=_('nombre'))
    last_name = models.CharField(max_length=256, verbose_name=_('apellido'))
    id_card_prefix = models.CharField(
        max_length=1, choices=ID_CARD_PREFIXES, default='V',
        verbose_name=_(u'prefijo de la cédula'))
    id_card_number = models.IntegerField(
        verbose_name=_(u'cédula de identidad'), null=True)
    picture = models.ImageField(
        upload_to=get_upload_path,
        null=True, blank=True, verbose_name=_('foto'))
    birth_date = models.DateField(verbose_name=_('fecha de nacimiento'))
    birth_place = models.CharField(
        max_length=256,
        default='', blank=True, verbose_name=_('lugar de nacimiento'))
    gender = models.CharField(
        max_length=1, choices=GENDERS, verbose_name=_('sexo'))
    dwelling = models.BooleanField(
        default=True, verbose_name=_(u'¿Posee vivienda?'))
    street = models.TextField(
        default='', blank=True, verbose_name=_(u'dirección'))
    phone_home = models.CharField(
        max_length=50,
        default='', blank=True, verbose_name=_(u'teléfono casa'))
    phone_mobile = models.CharField(
        max_length=50,
        default='', blank=True, verbose_name=_(u'teléfono móvil'))
    phone_office = models.CharField(
        max_length=50,
        default='', blank=True, verbose_name=_(u'teléfono oficina'))
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS,
        default='s', verbose_name=_('estado civil'))
    ses = models.ForeignKey(
        Ses,
        verbose_name=_(u'Estatus socioeconómico'), related_name='patients')
    occupation = models.ForeignKey(
        Occupation, related_name='patients', verbose_name=_(u'ocupación'))
    education = models.ForeignKey(
        Education, related_name='patients', verbose_name=_(u'educación'))
    personal_record = models.TextField(
        default='', blank=True, verbose_name=_(u'antecedentes patológicos'))
    family_record = models.TextField(
        default='', blank=True, verbose_name=_('antecedentes familiares'))
    habits = models.ManyToManyField(
        Habit,
        related_name='patients',
        blank=True, verbose_name=_(u'hábitos personales'))
    physical_exam = models.TextField(
        default='', blank=True, verbose_name=_(u'examen físico'))

    @classmethod
    def get_ordered_items(cls, order):
        if len(order) == 0:
            order = '-id'

        if order not in cls.ORDERING and \
                (order[0] == '-' and order[1:] not in cls.ORDERING):
            order = '-id'

        asc = '-' if order[0] == '-' else ''

        queryset = cls.objects.all()
        if order in ('name', '-name'):
            queryset = queryset.order_by(
                asc + 'last_name').order_by(asc + 'first_name')
        elif order in ('age', '-age'):
            queryset = queryset.order_by(
                ('' if asc == '-' else '-') + 'birth_date')
        elif order in ('creation', '-creation'):
            queryset = queryset.annotate(
                creation=Min('history__id')).order_by(asc + 'creation')
        elif order in ('modification', '-modification'):
            queryset = queryset.annotate(
                modification=Max(
                    'history__id')).order_by(asc + 'modification')
        elif order in ('id_card', '-id_card'):
            queryset = queryset.order_by(
                asc + 'id_card_prefix').order_by(asc + 'id_card_number')
        else:
            queryset = queryset.order_by(order)

        return queryset

    @property
    def full_name(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()

    @property
    def id_card(self):
        return '%s-%s' % (self.id_card_prefix, self.id_card_number)

    @property
    def age(self):
        today = timezone.now()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (
                self.birth_date.month, self.birth_date.day))

    @property
    def address(self):
        """
        :rtype: str
        :return:
        """
        return self.street

    @property
    def first_history(self):
        """
        :rtype apps.patients.models.History
        :return: first modification history object
        """
        if self.history.all().exists():
            return self.history.all().order_by('id')[0]
        else:
            return None

    @property
    def added_by(self):
        first_history = self.first_history
        return first_history.modified_by if first_history else None

    @property
    def last_history(self):
        """
        :rtype apps.patients.models.History
        :return: last modification history object
        """
        if self.history.all().exists():
            return self.history.all().order_by('-id')[0]
        else:
            return None

    def __str__(self):
        return self.full_name

    def get_last_channel(self, channel_type='r'):
        """
        Gets last Channel, by default it will returns last RR
        :rtype: apps.records.models.Channel
        :param channel_type: indicates
        what channel type is requesting, according to values specified in
        apps.records.models.Channel class
        :return: Channel
        """
        try:
            return self.records.order_by('id').last().channels.filter(
                type=channel_type).order_by('id').last()
        except AttributeError:
            return None

    class Meta:
        unique_together = ('id_card_prefix', 'id_card_number')
        verbose_name = _('paciente')
        ordering = ['-id']


@six.python_2_unicode_compatible
class History(models.Model):
    ALL = 'ALL'
    SEPARATOR = '[|]'

    modified_by = models.ForeignKey(
        'users.User',
        related_name='history', verbose_name=_('modificado por'))
    patient = models.ForeignKey(
        Patient, related_name='history', verbose_name=_('paciente'))
    date = models.DateTimeField(
        auto_now_add=True, verbose_name=_('fecha'))
    modified_field = models.TextField(
        default=ALL, verbose_name=_('campo modificado'))
    modified_old_value = models.TextField(
        default='', verbose_name=_('antiguo valor'))
    modified_new_value = models.TextField(
        default='', verbose_name=_('nuevo valor'))

    def __str__(self):
        return 'Patient: %s / M.D. %s' % (
            str(self.patient), self.modified_by.get_full_name())

    class Meta:
        verbose_name = _('historial de cambios')
        verbose_name_plural = _('historial de cambios')


@six.python_2_unicode_compatible
class Diagnosis(models.Model):
    patient = models.ForeignKey(
        Patient, related_name='diagnosis', verbose_name=_('paciente'))
    anomalies = models.ManyToManyField(
        'records.Anomaly', verbose_name=_(u'anomalías'))
    description = models.TextField(
        verbose_name=_(u'descripción'), default='', blank=True)
    made_by = models.ForeignKey(
        'users.User', null=True, verbose_name=_('Hecho por'))
    date = models.DateTimeField(
        auto_now_add=True, verbose_name=_(u'fecha de creación'), null=True)
    attachment = models.FileField(
        upload_to=get_upload_path,
        null=True, blank=True, verbose_name=_(u'Adjunto'))

    def __str__(self):
        return '%s - %s' % (self.patient, self.date)

    class Meta:
        verbose_name = _(u'diagnóstico')
        verbose_name_plural = _(u'diagnósticos')
