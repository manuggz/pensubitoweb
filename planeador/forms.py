# coding=utf-8
from django.forms import forms, CharField


class CrearNuevoPlanForm(forms.Form):
    nombre_plan = CharField(label="Nombre del Plan",help_text="Nombre del plan a crear.")
    archivo_html_expediente = forms.FileField(required=False,help_text="Archivo HTML de la página expediente.usb.ve.")