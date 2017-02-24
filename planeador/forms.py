from django.forms import forms, CharField


class CrearNuevoPlanForm(forms.Form):
    nombre_plan = CharField(initial="ads",label="Nombre del Plan",help_text="Jo Jo")
    archivo_html_expediente = forms.FileField(required=False)