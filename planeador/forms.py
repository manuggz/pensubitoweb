# coding=utf-8
import datetime
from django.forms import forms, CharField, Select, CheckboxInput, ChoiceField


## Form utilizado para cuando se va a crear un nuevo plan
from api_misvoti.models import CarreraUsb, PlanEstudioBase, TrimestrePlaneado


class CrearNuevoPlanForm(forms.Form):
    nombre_plan = CharField(label="Nombre del Plan",help_text="Nombre del plan a crear.")

    carrera_plan = ChoiceField(label=u'Carrera')
    plan_utilizar = ChoiceField(label=u"Plan a utilizar")

    ## Dice si se va a crear el plan usando el plan base de la carrera
    construir_usando_pb = CheckboxInput()

    ## El periodo - año de inicio indica:
    # Cuando el usuario crea un plan vacio- se le agrega un periodo por default con estos datos iniciales
    # Cuando se utiliza como base el plan de estudio de la carrera se comienza el llenado desde este periodo
    periodo_inicio = ChoiceField(label=u'Periodo inicio')
    anyo_inicio = ChoiceField(label=u"Año inicio")

    archivo_html_expediente = forms.FileField(required=False,help_text="Archivo HTML de la página expediente.usb.ve.")

    def __init__(self, *args, **kwargs):
        super(CrearNuevoPlanForm, self).__init__(*args, **kwargs)

        carreras_bd = CarreraUsb.objects.all()
        self.fields['carrera_plan'].choices = [ (c.pk, c.nombre) for c in carreras_bd ]

        get_nombre_tp = PlanEstudioBase.get_nombre_tipo_plan
        self.fields['plan_utilizar'].choices = [(pu.tipo, get_nombre_tp(pu)) for pu in PlanEstudioBase.objects.filter(carrera_fk=carreras_bd.first())]

        self.fields['periodo_inicio'].choices = [(p[0],p[1]) for p in    TrimestrePlaneado.PERIODOS_USB[:-1]]
        self.fields['anyo_inicio'].choices    = [(anyo,anyo) for anyo in xrange(1993,2030)]
        self.fields['anyo_inicio'].value    = datetime.datetime.now().year
        #self.fields['carrera_plan'].value = self.fields['carrera_plan'].choices[0][0]