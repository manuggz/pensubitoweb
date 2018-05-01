# coding=utf-8
import datetime

## Form utilizado para cuando se va a crear un nuevo plan
from django.forms import forms, CharField, ChoiceField, BooleanField, CheckboxInput

from api_misvoti.models import CarreraUsb, Pensum


class CrearNuevoPlanForm(forms.Form):
    nombre_plan = CharField(label="Nombre del Plan", help_text="Nombre del plan a crear.")

    carrera_plan = ChoiceField(label=u'Carrera')
    plan_utilizar = ChoiceField(label=u"Plan a utilizar")

    ## Dice si se va a crear el plan usando el plan base de la carrera
    construir_usando_pb = BooleanField(required=False)

    ## El periodo - año de inicio indica:
    # Cuando el usuario crea un plan vacio- se le agrega un periodo por default con estos datos iniciales
    # Cuando se utiliza como base el plan de estudio de la carrera se comienza el llenado desde este periodo
    # periodo_inicio = ChoiceField(label=u'Periodo inicio')
    anyo_inicio = ChoiceField(label=u"Año inicio")

    archivo_html_expediente = forms.FileField(required=False, help_text="Archivo HTML de la página expediente.usb.ve.")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CrearNuevoPlanForm, self).__init__(*args, **kwargs)

        carreras_bd = CarreraUsb.objects.all()
        self.fields['carrera_plan'].choices = [(c.pk, c.nombre) for c in carreras_bd]

        get_nombre_tp = Pensum.get_nombre_tipo_plan
        self.fields['plan_utilizar'].choices = [(pu.tipo, get_nombre_tp(pu)) for pu in
                                                Pensum.objects.filter(carrera=carreras_bd.first())]

        # self.fields['periodo_inicio'].choices = [(p[0],p[1]) for p in    TrimestrePlaneado.PERIODOS_USB[:-1]]
        self.fields['anyo_inicio'].choices = [(anyo, anyo) for anyo in range(1990, 2020)]

        self.fields['anyo_inicio'].value = datetime.datetime.now().year

        if self.user != None:
            if self.user.carnet:
                anyo_carnet = int(self.user.carnet[:2])
                print (anyo_carnet)
                if anyo_carnet >= 0 and anyo_carnet <= 90:
                    self.fields['anyo_inicio'].value = int("{0}{1}".format(20, anyo_carnet))
                else:
                    self.fields['anyo_inicio'].value = int("{0}{1}".format(19, anyo_carnet))

        self.fields['construir_usando_pb'].initial = True

        # self.fields['carrera_plan'].value = self.fields['carrera_plan'].choices[0][0]
