# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class TrimestreManager(models.Manager):
    def con_trimestres_ordenados(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return sorted(qs)

        ## Modelo para manejar el usuario del sistema


class MiVotiUser(AbstractUser):
    pass

class CarreraUsb(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return "CarreraUsb(" + self.nombre + "," + str(self.codigo) + ")"

    def __unicode__(self):
        return "CarreraUsb(" + self.nombre + "," + str(self.codigo) + ")"


## Plan de estudio creado por el usuario
# Un usuario puede crear multiples planes
class PlanEstudioBase(models.Model):
    PASANTIA = 'PA'
    PROYECTO_GRADO = 'PG'
    NO_DEFINIDO = 'ND'

    TIPO_PLAN = (
        (PASANTIA, 'Pasantia'),
        (PROYECTO_GRADO, 'Proyecto de grado a dedicación exclusiva'),
        (NO_DEFINIDO, 'No definido')
    )

    carrera_fk = models.ForeignKey(CarreraUsb)
    tipo = models.CharField(
        max_length=2,
        choices=TIPO_PLAN,
        default=NO_DEFINIDO,
    )

    def __str__(self):
        return self.carrera_fk.nombre +" " + self.tipo

    def __unicode__(self):
        return self.carrera_fk.nombre + " " + self.tipo


    def get_nombre_tipo_plan(self):
        for n,v in PlanEstudioBase.TIPO_PLAN:
            if n == self.tipo:
                return v
## Plan de estudio creado por el usuario
# Un usuario puede crear multiples planes
class PlanEstudio(models.Model):
    plan_estudio_base_fk = models.ForeignKey(PlanEstudioBase)
    nombre = models.CharField(max_length=200)
    usuario_creador_fk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "PlanEstudio(" + self.nombre + "," + str(self.usuario_creador_fk) + ")"

    def __unicode__(self):
        return "PlanEstudio(" + self.nombre + "," + str(self.usuario_creador_fk) + ")"


## Trimestre de un plan de estudio
## Este modelo basicamente dice un i abstracto al cual pueden referenciar
# multiples planes de distintos usuarios


## Representa un i con los datos reales de curso de un usuario particular
# Por ejemplo: fotos del i, notas particulares,...
class TrimestrePlaneado(models.Model):
    SEPTIEMBRE_DICIEMBRE = 'SD'
    ENERO_MARZO = 'EM'
    ABRIL_JULIO = 'AJ'
    JULIO_AGOSTO = 'JA'

    PERIODOS_USB = (
        (SEPTIEMBRE_DICIEMBRE, 'Septiembre - Diciembre'),
        (ENERO_MARZO, 'Enero - Marzo'),
        (ABRIL_JULIO, 'Abril - Julio'),
        (JULIO_AGOSTO, 'Intensivo(Julio - Agosto)'),
    )

    periodo = models.CharField(
        max_length=2,
        choices=PERIODOS_USB,
        default=SEPTIEMBRE_DICIEMBRE,
    )
    anyo = models.CharField(max_length=5)
    planestudio_pert_fk = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE)
    objects = TrimestreManager()

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __cmp__(self, other):
        if not isinstance(other, TrimestrePlaneado): return
        if int(self.anyo) < int(other.anyo):
            return -1
        elif int(self.anyo) > int(other.anyo):
            return 1
        else:
            if self.periodo == other.periodo:
                return 0
            else:
                if self.periodo == TrimestrePlaneado.ENERO_MARZO:
                    return -1
                elif self.periodo == TrimestrePlaneado.ABRIL_JULIO:
                    if other.periodo == TrimestrePlaneado.ENERO_MARZO:
                        return 1
                    else:
                        return -1
                elif self.periodo == TrimestrePlaneado.JULIO_AGOSTO:
                    if other.periodo == TrimestrePlaneado.SEPTIEMBRE_DICIEMBRE:
                        return -1
                    else:
                        return 1
                elif self.periodo == TrimestrePlaneado.SEPTIEMBRE_DICIEMBRE:
                    return 1

    def __str__(self):
        return self.periodo + " " + self.anyo + str(self.planestudio_pert_fk) + ")"

    def __unicode__(self):
        return self.periodo + " " + self.anyo + str(self.planestudio_pert_fk) + ")"


# class DepartamentoUSB(models.Model):
#     nombre = models.CharField(max_length=200)
#     codigo = models.CharField(max_length=5, primary_key=True)
#
#     def __str__(self):
#         return "Departamento(" + self.nombre + "," + self.codigo + ")"
#
#     def __unicode__(self):
#         return "Departamento(" + self.nombre + "," + self.codigo + ")"


## Representa una materia de la misma forma que TrimestreBase representa un i
# Este modelo puede ser referenciado por multiples planes de distintos usuarios
# Por lo que puede usarse para guardar datos generales para todos los usuarios/planes
class MateriaBase(models.Model):
    POSIBLES_CREDITOS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    nombre = models.CharField(max_length=200,null=True)
    codigo = models.CharField(max_length=10,primary_key=True)
    creditos = models.CharField(
        max_length=1,
        choices=POSIBLES_CREDITOS,
        default='1',
    )

    # departamento_fk = models.ForeignKey(DepartamentoUSB,null=True)

    def __str__(self):
        return self.nombre + " - " + self.codigo


    def __unicode__(self):
        return self.nombre + " - " + self.codigo


# Representa una materia con los datos particulares de cuando un usuario la va a cursar o la cursó
class MateriaPlaneada(models.Model):
    POSIBLES_NOTAS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    trimestre_cursada_fk = models.ForeignKey(TrimestrePlaneado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200,null=True)
    codigo = models.CharField(max_length=10)
    creditos = models.CharField(
        max_length=1,
        choices=MateriaBase.POSIBLES_CREDITOS,
        default='1',
    )
    nota_final = models.CharField(
        max_length=1,
        choices=POSIBLES_NOTAS,
        default='1',
    )
    esta_retirada = models.BooleanField(default=False)


    def __str__(self):
        return self.codigo + " " + str(self.trimestre_cursada_fk) + ")"

    def __unicode__(self):
        return self.codigo + " " + str(self.trimestre_cursada_fk) + ")"
