from django.contrib import admin

# Register your models here.
from api_misvoti.models import *
from planeador.models import *

admin.site.register(MiVotiUser)
admin.site.register(PlanCreado)
admin.site.register(TrimestrePlaneado)
admin.site.register(TrimestrePensum)
admin.site.register(MateriaPlaneada)
admin.site.register(MateriaBase)
admin.site.register(Pensum)
admin.site.register(CarreraUsb)
