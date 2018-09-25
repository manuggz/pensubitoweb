# coding=utf-8
import json
import os
import re

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from api_misvoti.models import RelacionMateriaPensumBase, TrimestrePensum, Pensum
from planeador.constants import *
from planeador.gdrive_namespaces import ID_DRIVE_CARPETA_MIS_VOTI

## Pattern para validar los códigos de las materias
pattern_codigo_materia = re.compile("^[a-zA-Z]{2,4}-?\d{3,4}$")


# ## Define una
# class MateriaUsuario(object):
#
#     def __init__(self,tipo,creditos=None,horas_teoria=None,horas_practica=None,horas_laboratorio=None,nombre=None,codigo=None,nota_final=None,esta_retirada=False):
#         self.creditos = creditos
#         self.horas_teoria = horas_teoria
#         self.horas_practica = horas_practica
#         self.horas_laboratorio = horas_laboratorio
#         self.nombre = nombre
#         self.codigo = codigo
#         self.tipo  = tipo
#         self.nota_final = nota_final
#         self.esta_retirada = esta_retirada
#
#
# class TrimestreUsuario(object):
#
#     def __init__(self,periodo,anyo,materias):
#         self.periodo = periodo
#         self.anyo = anyo
#         self.materias = materias
#
# class PlanEstudioUsuario(object):
#     def __init__(self, nombre, trimestres,id_pensum):
#         self.nombre = nombre
#         self.trimestres = trimestres
#         self.id_pensum = id_pensum

## Estos Serializadores son los encargados de Parsear el JSON que es mandado por los usuarios del API
## El JSON es de la forma {nombre:string,id_pensum:int,trimestres:[{periodo:string,anyo:int,materias:[{creditos...}]}]}

## Serializador Para las Materas
class MateriaUsuarioSerializer(serializers.Serializer):
    creditos = serializers.IntegerField(required=False, min_value=1, max_value=9)
    horas_teoria = serializers.IntegerField(required=False, min_value=0)
    horas_practica = serializers.IntegerField(required=False, min_value=0)
    horas_laboratorio = serializers.IntegerField(required=False, min_value=0)
    nombre = serializers.CharField(required=False,allow_blank=True)
    codigo = serializers.CharField(required=False,allow_blank=True)
    tipo = serializers.ChoiceField(POSIBLES_TIPOS)
    nota_final = serializers.IntegerField(required=False, min_value=1, max_value=5,allow_null=True)
    esta_retirada = serializers.BooleanField(default=False)

    ## Es ejecutado automáticamente para validar el código de las materias en el JSON
    def validate_codigo(self, value):

        if value == "": return ""

        if pattern_codigo_materia.match(value):
            return value

        raise serializers.ValidationError("¡Codigo de Materia Inválido!")


class TrimestreUsuarioSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(TrimestrePensum.PERIODOS_USB)
    anyo = serializers.IntegerField(min_value=1900, max_value=3000)
    materias = MateriaUsuarioSerializer(many=True)


class PlanEstudioUsuarioSerializer(serializers.Serializer):
    #nombre = serializers.CharField()
    trimestres = TrimestreUsuarioSerializer(many=True)
    id_pensum = serializers.IntegerField()

    ## Valida el Id del Pensum buscando una Pensum en la BD que tenga un pk igual al id pasado
    ## Esto implica que el usuario debe saber los id's de los pensums que contiene la BD
    ## TODO : Por lo que, Se debe proveer una parte donde el usuario pueda obtener los pensums
    def validate_id_pensum(self, value):

        try:
            Pensum.objects.get(pk=value)
            return value
        except ObjectDoesNotExist:
            raise serializers.ValidationError("¡Código de Pensum Inválido!")

    ## Guarda el Pensum -> Crea el archivo en la carpeta del drive
    def save(self, user):
        ruta_local = os.path.join('planes_json_cache', user.gdrive_id_json_plan)

        # Eliminamos la Copia Local
        if os.path.exists(ruta_local):
            os.remove(ruta_local)

        # Obtenemos la referencia al archivo en Google Drive
        if user.gdrive_id_json_plan:
            gdrive_file = apps.get_app_config('planeador').g_drive.CreateFile({'id': user.gdrive_id_json_plan})
        else:
            ## Creamos un nuevo archivo en google Drive
            gdrive_file = apps.get_app_config('planeador').g_drive.CreateFile(
                {'title': user.username + '_plan', 'parents': [
                    {
                        "kind": "drive#parentReference",
                        'id': ID_DRIVE_CARPETA_MIS_VOTI
                    }
                ]})

        ## Establece el contenido
        gdrive_file.SetContentString(json.dumps(self.validated_data))
        # Upload the file.
        gdrive_file.Upload()

        user.gdrive_id_json_plan = gdrive_file['id']
        user.save()
