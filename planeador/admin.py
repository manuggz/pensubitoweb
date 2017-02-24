from django.contrib import admin

# Register your models here.
from planeador.models import MiVotiUser, PlanEstudio, TrimestreBase, TrimestrePlaneado, MateriaBase, MateriaPlaneada

admin.site.register(MiVotiUser)
admin.site.register(PlanEstudio)
admin.site.register(TrimestreBase)
admin.site.register(TrimestrePlaneado)
admin.site.register(MateriaBase)
admin.site.register(MateriaPlaneada)