# coding=utf-8
import json
import os

import re
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import request
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from api_misvoti.models import RelacionMateriaPensumBase, TrimestrePensum, Pensum
from planeador.gdrive_namespaces import ID_DRIVE_CARPETA_MIS_VOTI

pattern_codigo_materia = re.compile("^[a-zA-Z]{2,4}-?\d{3,4}$")

class MateriaUsuario(object):

    def __init__(self,tipo,creditos=None,horas_teoria=None,horas_practica=None,horas_laboratorio=None,nombre=None,codigo=None,nota_final=None,esta_retirada=False):
        self.creditos = creditos
        self.horas_teoria = horas_teoria
        self.horas_practica = horas_practica
        self.horas_laboratorio = horas_laboratorio
        self.nombre = nombre
        self.codigo = codigo
        self.tipo  = tipo
        self.nota_final = nota_final
        self.esta_retirada = esta_retirada


class TrimestreUsuario(object):

    def __init__(self,periodo,anyo,materias):
        self.periodo = periodo
        self.anyo = anyo
        self.materias = materias

class PlanEstudioUsuario(object):
    def __init__(self, nombre, trimestres,id_pensum):
        self.nombre = nombre
        self.trimestres = trimestres
        self.id_pensum = id_pensum

class MateriaUsuarioSerializer(serializers.Serializer):

    creditos = serializers.IntegerField(required=False,min_value=1,max_value=9)
    horas_teoria = serializers.IntegerField(required=False,min_value=0)
    horas_practica = serializers.IntegerField(required=False,min_value=0)
    horas_laboratorio = serializers.IntegerField(required=False,min_value=0)
    nombre = serializers.CharField(required=False)
    codigo = serializers.CharField(required=False)
    tipo = serializers.ChoiceField(RelacionMateriaPensumBase.POSIBLES_TIPOS)
    nota_final = serializers.IntegerField(required=False,min_value=1,max_value=5)
    esta_retirada = serializers.BooleanField(default=False)

    def validate_codigo(self,value):

        if pattern_codigo_materia.match(value):
            return value

        raise serializers.ValidationError("¡Codigo de Materia Inválido!")

class TrimestreUsuarioSerializer(serializers.Serializer):
    periodo = serializers.ChoiceField(TrimestrePensum.PERIODOS_USB)
    anyo = serializers.IntegerField(min_value=1900,max_value=3000)
    materias = MateriaUsuarioSerializer(many=True)


class PlanEstudioUsuarioSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    trimestres = TrimestreUsuarioSerializer(many=True)
    id_pensum = serializers.IntegerField()

    def validate_id_pensum(self,value):

        try:
            Pensum.objects.get(pk=value)
            return value
        except ObjectDoesNotExist:
            raise serializers.ValidationError("¡Código de Pensum Inválido!")

    def save(self,user):
        print 'validado:',self.validated_data
        ruta_local = os.path.join('planes_json_cache',user.gdrive_id_json_plan)

        #Eliminamos la Copia Local
        if os.path.exists(ruta_local):
          os.remove(ruta_local)

        #Obtenemos la referencia al archivo en Google Drive
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
        gdrive_file.Upload()  # Upload the file.

        user.gdrive_id_json_plan = gdrive_file['id']
        user.save()
