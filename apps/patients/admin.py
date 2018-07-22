from apps.patients.forms import PatientAdminForm
import apps.patients.models as models
from utils.admin import register_models
from django.contrib import admin


class PatientModelAdmin(admin.ModelAdmin):
    form = PatientAdminForm


admins = {
    models.Patient.__name__: PatientModelAdmin
}

register_models(models, admins)
