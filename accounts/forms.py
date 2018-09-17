from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import CharField, EmailField, IntegerField, ChoiceField

from api_misvoti.models import Pensum


class ProfileSettingsForm(forms.Form):
    name = CharField(max_length=30, required=False)
    last_name = CharField(max_length=150, required=False)
    email = EmailField(label="Correo",required=False)
    usbid = CharField(max_length=10, required=False)

    starting_year = IntegerField(min_value=1999,max_value=2999)
    pensum = ChoiceField(label=u"Pensum")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileSettingsForm, self).__init__(*args, **kwargs)

        pensums_bd = Pensum.objects.all()
        self.fields['pensum'].choices = [(c.pk, c.carrera.nombre + " ( " + c.get_nombre_tipo_plan() + " )") for c in
                                         pensums_bd]
        self.fields['pensum'].widget.attrs['class'] = 'form-control selectpicker show-tick show-menu-arrow'
        self.fields['pensum'].widget.attrs['title'] = 'Escoja un pensum.'

        if self.user is not None:
            self.fields['name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['usbid'].initial = self.user.usbid
            self.fields['starting_year'].initial = self.user.anyo_inicio

            try:
                user_pensum = Pensum.objects.get(carrera__codigo=self.user.codigo_carrera, tipo = self.user.tipo_pensum)
                self.fields['pensum'].initial = user_pensum.pk
            except ObjectDoesNotExist:
                pass



