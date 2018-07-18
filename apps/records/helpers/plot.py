# coding=utf-8
import matplotlib.pyplot as plt
from django.utils.translation import ugettext as _
from numpy import random


def get_channel_points(channel, interval_start, interval_end):
    x = []
    y = []
    kwargs = {
        ('x__gte' if not channel.is_time else 'y_accumulative__gte'):
        interval_start if channel.is_time else
        interval_start / channel.sampling_rate
    }
    if interval_end not in (None, ''):
        kwargs['x__lte' if not channel.is_time else 'y_accumulative__lte'] = \
            interval_end if channel.is_time else\
            interval_end / channel.sampling_rate

    points = channel.points.filter(**kwargs).order_by('x')

    for point in points:
        x.append(point.x)
        y.append(point.y)

    return x, y


def get_all_channel_points(channel):
    x = []
    y = []
    [(
        x.append(point.x),
        y.append(point.y)
    ) for point in channel.points.all().order_by('x')]

    return x, y


def get_channel_image(channel, file_like, format_='png', interval_start=0,
                      interval_end=None, clear=True, color='r', line_style='-'):
    x, y = get_channel_points(channel, interval_start, interval_end)

    get_image(
        x,
        y,
        file_like,
        _(u'Señal') if channel.type != 'r' else _(
            'Serie temporal de intervalos RR'),
        format_=format_,
        ylabel=_('Tiempo (ms)') if channel.is_time else None,
        xlabel=_('Secuencia') if channel.is_time else 'ms',
        hide_axis=not channel.is_time,
        color=color,
        line_style=line_style,
        clear=clear
    )


def get_media_image(channel, file_like, initial_time, final_time,
                    interval, format_='png', clear=True, color='r',
                    line_style='-', label=None, title=None):
    x, y = channel.get_media_points(initial_time, final_time, interval)
    get_image(
        x,
        y,
        file_like,
        'RR Media: %s' % channel.record.patient.full_name if title is None else
        title,
        format_=format_,
        ylabel=_('Media (ms)'),
        xlabel=_('Intervalo (%(interval)d m)') % {'interval': interval / 60000},
        hide_axis=not channel.is_time,
        clear=clear,
        color=color,
        line_style=line_style,
        label=channel.record.patient.full_name if label is None else label
    )


def get_standard_deviation_image(channel, file_like, initial_time, final_time,
                                 interval, format_='png', clear=True,
                                 color='r', line_style='-', label=None,
                                 title=None):
    x, y = channel.get_standard_deviation_points(
        initial_time, final_time, interval)
    get_image(
        x,
        y,
        file_like,
        (_(u'RR Desviación estándar: %(patient)s') % {
            'patient': channel.record.patient.full_name
        }) if title is None else title,
        format_=format_,
        ylabel=_('STD (ms)'),
        xlabel=_('Intervalo (%(interval)d m)') % {'interval': interval / 60000},
        hide_axis=not channel.is_time,
        clear=clear,
        color=color,
        line_style=line_style,
        label=channel.record.patient.full_name if label is None else label
    )


def get_return_map_image(channel, file_like, initial_time, final_time,
                         format_='png', clear=True, color='r', line_style='.',
                         title=None, label=None):
    x, y = channel.get_return_map(initial_time, final_time)
    get_image(
        x,
        y,
        file_like,
        (_('RR Mapa de retorno: %(patient)s') % {
            'patient': channel.record.patient.full_name
        }) if title is None else title,
        format_=format_,
        ylabel=_('$RR_{t + 1} (ms)$'),
        xlabel=_('$RR_t (ms)$'),
        hide_axis=not channel.is_time,
        clear=clear,
        color=color,
        line_style=line_style,
        label=channel.record.patient.full_name if label is None else label
    )


def get_SDSD_image(channel, file_like, initial_time, final_time, interval,
                   format_='png', clear=True, color='r', line_style='-',
                   label=None, title=None):
    x, y = channel.get_SDSD(initial_time, final_time, interval)
    get_image(
        x,
        y,
        file_like,
        (_(u'RR SDSD: %(patient)s') % {
            'patient': channel.record.patient.full_name
        }) if title is None else title,
        format_=format_,
        ylabel=_('SDSD (ms)'),
        xlabel=_('Intervalo (%(interval)d m)') % {'interval': interval / 60000},
        hide_axis=not channel.is_time,
        clear=clear,
        color=color,
        line_style=line_style,
        label=channel.record.patient.full_name if label is None else label
    )


def get_PNN50_image(channel, file_like, initial_time, final_time, interval,
                    format_='png', clear=True, color='r', line_style='-',
                    label=None, title=None):
    x, y = channel.get_PNN50(initial_time, final_time, interval)
    get_image(
        x,
        y,
        file_like,
        (_(u'RR PNN50: %(patient)s') % {
            'patient': channel.record.patient.full_name
        }) if title is None else title,
        format_=format_,
        ylabel=_('PNN50 (ms)'),
        xlabel=_('Intervalo (%(interval)d m)') % {'interval': interval / 60000},
        hide_axis=not channel.is_time,
        clear=clear,
        color=color,
        line_style=line_style,
        label=channel.record.patient.full_name if label is None else label
    )


def get_fft_image(channel, file_like, initial_time, final_time, interval,  # noqa
                  format_='png', clear=True, color='r', line_style='-',
                  label=None, title=None):
    lf, hf, power, relation, x = channel.get_fft(
        initial_time, final_time, interval)
    format_ = format_
    ylabel = _('(un)')
    xlabel = _('Intervalo (%(interval)d m)') % {'interval': interval / 60000}
    hide_axis = not channel.is_time
    clear = clear
    color = color
    line_style = line_style
    label = channel.record.patient.full_name if label is None else label
    title = (_(u'RR FFT: %(patient)s') % {
                'patient': channel.record.patient.full_name
            }) if title is None else title
    if clear:
        plt.clf()

    plt.subplot(3, 1, 1)
    if len(x) > 0:
        plt.xlim(min(x), max(x))

    if title:
        plt.title(title)

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.plot(
        x, lf,
        'o',
        linestyle='solid',
        color='blue', label=_('LF (un)'))
    plt.plot(
        x, hf,
        'o',
        linestyle='solid',
        color='red', label=_('HF(un)'))
    plt.legend()
    plt.subplot(3, 1, 2)
    plt.plot(
        x, power,
        linestyle='solid',
        color='green', label=_('Potencia'))

    plt.legend()

    if len(x) > 0:
        plt.xlim(min(x), max(x))

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel('$ms^2$')

    plt.subplot(3, 1, 3)
    plt.plot(
        x, relation,
        linestyle='solid',
        color='magenta', label=_(u'Relación LF/HF'))
    plt.legend()

    if len(x) > 0:
        plt.xlim(min(x), max(x))

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(_('LF(un)/HF(un)'))

    fig = plt.figure()
    fig.gca()
    plt.figure(1)

    plt.grid(False)

    if hide_axis:
        # plt.axis('off')
        plt.tick_params(
                axis='both',
                which='both',
                bottom='off',
                top='off',
                labelbottom='off',
                left='off',
                labelleft=False)
    # fig.savefig(file_like, format=format_)
    if file_like is not None:
        plt.tight_layout()
        plt.savefig(file_like, format=format_, bbox_inches='tight')
        plt.show()


def get_histogram(channel, initial_time, final_time, file_like, bins=10,
                  title=None, format_='png', xlabel=None, ylabel=None,
                  line_style='-', hide_axis=False, clear=True, color='r'):
    points = channel.points.filter(y_accumulative__gte=initial_time,
                                   y_accumulative__lte=final_time)
    if title is None:
        title = _(u'RR Histograma: %(patient)s') % {
            'patient': channel.record.patient.full_name
        }
    plt.clf()
    plt.hist([point.y for point in points], bins)
    plt.xlabel(xlabel if xlabel is not None else _('$RR_t (ms)$'))
    plt.ylabel(
        ylabel if ylabel is not None else _(u'Frecuencia (cantidad)'))
    plt.title(title)
    plt.grid(True)
    if file_like is not None:
        plt.tight_layout()
        plt.savefig(file_like, format=format_, bbox_inches='tight')
        plt.show()


def get_all_images(channel, file_like, initial_time, final_time, interval,
                   format_='png', clear=True, color=None, line_style='-',
                   label=None, title=None):
    if clear:
        plt.clf()
    plt.figure(1)

    # config
    LABEL_SIZE = 5

    # All signal

    x, y = get_all_channel_points(channel)
    ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2)
    ax1.plot(x, y, line_style,
             color=random.rand(3, 1), label=None)
    ax1.grid(False)
    ax1.set_xlim([min(x), max(x)])
    ax1.set_ylabel(_('Tiempo (ms)') if channel.is_time else None)
    ax1.set_xlabel(_('Secuencia') if channel.is_time else 'ms')
    ax1.tick_params(axis='both', which='major', labelsize=LABEL_SIZE + 3)

    # Signal
    x, y = get_channel_points(channel, initial_time, final_time)
    # setting background for our interval
    ax1.axvspan(min(x), max(x), facecolor='b', alpha=0.5)
    ax2 = plt.subplot2grid((4, 2), (1, 0))
    ax2.plot(x, y, line_style,
             color=random.rand(3, 1), label=label if label else _(u'Señal'))
    ax2.set_title(
        _(u'Señal') if channel.type != 'r' else _('Serie temporal RR'))
    ax2.grid(True)
    ax2.set_xlim([min(x), max(x)])
    ax2.set_ylabel(_('Tiempo (ms)') if channel.is_time else None)
    ax2.set_xlabel(_('Secuencia') if channel.is_time else 'ms')
    ax2.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    # Media
    x, y = channel.get_media_points(initial_time, final_time, interval)
    ax3 = plt.subplot2grid((4, 2), (1, 1))
    ax3.plot(x, y, line_style,
             color=random.rand(3, 1), label=label if label else _(u'Media'))
    ax3.set_title(_('Media'))
    ax3.grid(True)
    ax3.set_xlim([min(x), max(x)])
    ax3.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax3.set_ylabel(_('Media (ms)') if channel.is_time else None)
    ax3.set_xlabel(
        _('Intervalo (%(interval)d m)') % {'interval': interval / 60000})
    # STD
    x, y = channel.get_standard_deviation_points(
        initial_time, final_time, interval)
    ax4 = plt.subplot2grid((4, 2), (2, 0))
    ax4.set_title(_(u'Desviación estándar'))
    ax4.grid(True)
    ax4.plot(x, y, line_style,
             color=random.rand(3, 1), label=label if label else '')
    ax4.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax4.set_ylabel(_('STD (ms)') if channel.is_time else None)
    ax4.set_xlabel(
        _('Intervalo (%(interval)d m)') % {'interval': interval / 60000})
    # Return map
    x, y = channel.get_return_map(initial_time, final_time)
    ax5 = plt.subplot2grid((4, 2), (2, 1))
    ax5.set_title(_('Mapa de retorno'))
    ax5.grid(True)
    ax5.plot(x, y, '.', color=random.rand(3, 1), label=label if label else '')
    ax5.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax5.set_ylabel('$RR_{t + 1} (ms)$')
    ax5.set_xlabel('$RR_t (ms)$')
    # SDSD
    x, y = channel.get_SDSD(initial_time, final_time, interval)
    ax6 = plt.subplot2grid((4, 2), (3, 0))
    ax6.set_title(_('rMSSD o SDSD'))
    ax6.grid(True)
    ax6.plot(x, y, line_style, color=random.rand(3, 1),
             label=label if label else '')
    ax6.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax6.set_ylabel(_('SDSD (ms)'))
    ax6.set_xlabel(
        _('Intervalo (%(interval)d m)') % {'interval': interval / 60000})
    # PNN50
    x, y = channel.get_PNN50_points(
        initial_time, final_time, interval)
    ax7 = plt.subplot2grid((4, 2), (3, 1))
    ax7.set_title(_('PNN50'))
    ax7.grid(True)
    ax7.plot(x, y, line_style, color=random.rand(3, 1),
             label=label if label else '')
    ax7.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax7.set_ylabel('PNN50 (ms)')
    ax7.set_xlabel(
        _('Intervalo (%(interval)d m)') % {'interval': interval / 60000})

    # Finally drawing
    plt.tight_layout()
    if file_like is not None:
        plt.savefig(file_like, format=format_, bbox_inches='tight')


def get_image(x, y, file_like=None, title=None, format_='png', xlabel=None,
              ylabel=None, line_style='-', hide_axis=False, clear=True,
              color='r', label=None):
    if clear:
        plt.clf()
    plt.plot(x, y, line_style, color=color, label=label if label else '')
    plt.legend()
    if len(x) > 0:
        plt.xlim(min(x), max(x))
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    fig = plt.figure()
    fig.gca()
    plt.figure(1)

    plt.grid(True)

    if hide_axis:
        # plt.axis('off')
        plt.tick_params(
                axis='both',
                which='both',
                bottom='off',
                top='off',
                labelbottom='off',
                left='off',
                labelleft=False)
    # fig.savefig(file_like, format=format_)
    if file_like is not None:
        plt.tight_layout()
        plt.savefig(file_like, format=format_, bbox_inches='tight')
        plt.show()


def save(file_like, format_='png'):
    if file_like is not None:
        plt.tight_layout()
        plt.savefig(file_like, format=format_, bbox_inches='tight')
        plt.show()
    plt.clf()


if __name__ == '__main__':
    get_channel_image(None, 'test.png')
