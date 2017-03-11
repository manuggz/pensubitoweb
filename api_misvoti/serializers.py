# coding=utf-8
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.reverse import reverse
from rest_framework.utils import model_meta

from api_misvoti.fields_serializer import PlanEstudioCreadoUrl
from api_misvoti.models import MiVotiUser, PlanCreado, TrimestrePlaneado, MateriaPlaneada, PlanEstudioBase


class UserSerializer(serializers.ModelSerializer):
    planes_creados = serializers.PrimaryKeyRelatedField(read_only=True,many=True)

    class Meta:
        model = MiVotiUser
        fields = ('username', 'forma_acceso', 'carnet', 'estan_cargados_datos_ldap', 'cedula', 'tipo', 'planes_creados')


class MateriaCreadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MateriaPlaneada
        exclude = ('trimestre_cursada_fk',)


class TrimestreCreadoSerializer(serializers.ModelSerializer):
    materias_planeadas = MateriaCreadaSerializer(
        many=True,
    )
    class Meta:
        model = TrimestrePlaneado
        fields = ('id','periodo','anyo','materias_planeadas')

class PlanUserEstudioSerializer(serializers.ModelSerializer):
    #trimestres_planeados = serializers.HyperlinkedIdentityField('trimestre-detail')

    plan_base = serializers.StringRelatedField(source='plan_estudio_base_fk',read_only=True)
    datos = serializers.ReadOnlyField(source='obtener_datos_analisis')
    url = serializers.HyperlinkedIdentityField('planescreados-detail')

    class Meta:
        model = PlanCreado
        fields = ('id','url' ,'nombre', 'plan_base','datos')


class PlanEstudioSerializer(serializers.ModelSerializer):
    trimestres_planeados = TrimestreCreadoSerializer(
        many=True,
    )

    propietario = serializers.ReadOnlyField(source='usuario_creador_fk.username')
    plan_base = serializers.StringRelatedField(source='plan_estudio_base_fk',read_only=True)

    class Meta:
        model = PlanCreado
        fields = ('id','nombre','propietario','plan_base','trimestres_planeados')

    def create(self, validated_data):
        trimestres_planeados_data = validated_data.pop('trimestres_planeados')
        plan_bd = PlanCreado.objects.create(**validated_data)
        for trimestre_json in trimestres_planeados_data:
            trimestre_bd = TrimestrePlaneado(
                planestudio_pert_fk=plan_bd,
                periodo=trimestre_json['periodo'],
                anyo=trimestre_json['anyo'],
            )
            trimestre_bd.save()

            for materia_json in trimestre_json['materias_planeadas']:
                materia_bd = MateriaPlaneada(
                    **materia_json
                )
                materia_bd.trimestre_cursada_fk = trimestre_bd
                materia_bd.save()

        return plan_bd


    def update(self, plan_bd, validated_data):
        print plan_bd
        print validated_data

        ## Alerta eliminamos todos los trimestres anteriores! No hacer en CASA
        TrimestrePlaneado.objects.filter(planestudio_pert_fk=plan_bd).delete()

        plan_bd.nombre = validated_data['nombre']
        plan_bd.save()

        for trimestre_json in validated_data['trimestres_planeados']:
            trimestre_bd = TrimestrePlaneado(
                planestudio_pert_fk=plan_bd,
                periodo=trimestre_json['periodo'],
                anyo=trimestre_json['anyo'],
            )
            trimestre_bd.save()

            for materia_json in trimestre_json['materias_planeadas']:
                materia_bd = MateriaPlaneada(
                    **materia_json
                )
                materia_bd.trimestre_cursada_fk = trimestre_bd
                materia_bd.save()


        return plan_bd
