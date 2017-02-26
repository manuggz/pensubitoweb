from django.contrib import admin

# Register your models here.
from planeador.models import MiVotiUser, PlanEstudio, TrimestreBase, TrimestrePlaneado, MateriaBase, MateriaPlaneada, \
    Prerequisito, Correquisito, DepartamentoUSB, PlanEstudioBase, CarreraUsb

admin.site.register(MiVotiUser)
admin.site.register(PlanEstudio)
admin.site.register(TrimestreBase)
admin.site.register(TrimestrePlaneado)
admin.site.register(MateriaBase)
admin.site.register(MateriaPlaneada)
admin.site.register(Prerequisito)
admin.site.register(Correquisito)
admin.site.register(DepartamentoUSB)
admin.site.register(PlanEstudioBase)
admin.site.register(CarreraUsb)
