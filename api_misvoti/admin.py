from django.contrib import admin

from api_misvoti.models import *

admin.site.register(MiVotiUser)
admin.site.register(MateriaBase)
admin.site.register(Pensum)
admin.site.register(CarreraUsb)
admin.site.register(TrimestrePensum)
admin.site.register(RelacionMateriaPensumBase)
admin.site.register(RelacionMateriaPrerrequisito)
admin.site.register(RelacionMateriasCorrequisito)
admin.site.register(RelacionMateriaOpcional)