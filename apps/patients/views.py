from apps.patients.forms import PatientForm
from apps.patients.models import Patient, History
from django.core.urlresolvers import reverse
from django.db.models import Model
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.contrib import messages
from django.utils.translation import ugettext as _
from faker import Factory

fake = Factory.create()

# Create your views here.
from django.template.context import RequestContext


class PatientList(View):
    form_class = PatientForm

    def get(self, request):
        data = {
            'patients': Patient.objects.all()
        }
        return HttpResponse(render(request, 'patient_list.html',
                                   context=RequestContext(request, data)))

    def post(self, request):
        """
        Process user creation
        :param request:
        :return:
        """
        # processing form
        form = self.form_class(request.POST, request.FILES)

        patient = None
        if form.is_valid():
            patient = form.save()
            History.objects.create(
                modified_by=request.user,
                patient=patient
            )
            messages.success(
                request,
                _('Los datos del paciente %(name)s han sido guardados &eacute;xitosamente') % {'name': patient.full_name})
            return HttpResponseRedirect(reverse('patient_detail', args=(patient.id,)))

        data = {
            'patient': patient,
            'form': form
        }
        return HttpResponse(render(request, 'patient_detail.html', context=RequestContext(request, data)))


class PatientDetail(View):
    form_class = PatientForm

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        return HttpResponse(render(request, 'patient_detail.html',
                                   context=RequestContext(request, {'patient': patient})))

    def post(self, request, patient_id):
        """
        Saves an user edit
        :param request:
        :param patient_id:
        :return:
        """
        patient = get_object_or_404(Patient, id=patient_id)
        # processing form
        form = self.form_class(request.POST, request.FILES, instance=patient)

        if form.is_valid():
            patient = form.save()
            for changed in form.changed_data:
                History.objects.create(
                    modified_by=request.user,
                    patient=patient,
                    modified_field=changed,
                    modified_old_value=str(form.initial[changed]) if not isinstance(form.initial[changed], Model) else str(form.initial[changed].id),
                    modified_new_value=str(form.cleaned_data[changed]) if not isinstance(form.cleaned_data[changed], Model) else str(form.cleaned_data[changed].id)
                )
            messages.success(
                request,
                _('Los datos del paciente %(name)s han sido guardados &eacute;xitosamente') % {
                    'name': patient.full_name
                })
            return HttpResponseRedirect(reverse('patient_detail', args=(patient.id,)))

        data = {
            'patient': patient,
            'form': form
        }
        return HttpResponse(render(request, 'patient_detail.html', context=RequestContext(request, data)))


class PatientEdit(View):
    form_class = PatientForm

    def get(self, request, patient_id):
        """
        Shows patient edit form
        :param request:
        :param patient_id:
        :return:
        """
        patient = get_object_or_404(Patient, id=patient_id)
        form = self.form_class(instance=patient)
        data = {
            'patient': patient,
            'form': form
        }
        return HttpResponse(render(request, 'patient_detail.html', context=RequestContext(request, data)))


class PatientNew(View):
    form_class = PatientForm

    def get(self, request):
        """
        Shows patient creation form
        :param request:
        :return:
        """
        form = self.form_class()
        data = {
            'form': form
        }
        return HttpResponse(render(request, 'patient_detail.html', context=RequestContext(request, data)))
