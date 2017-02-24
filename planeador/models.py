# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

## Modelo para manejar el usuario del sistema
class MiVotiUser(AbstractUser):
    pass

## Plan de estudio creado por el usuario
# Un usuario puede crear multiples planes
class PlanEstudio(models.Model):
    nombre = models.CharField(max_length=200)
    usuario_creador_fk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


## Trimestre de un plan de estudio
## Este modelo basicamente dice un trimestre abstracto al cual pueden referenciar
# multiples planes de distintos usuarios
class TrimestreBase(models.Model):

    SEPTIEMBRE_DICIEMBRE = 'SD'
    ENERO_MARZO = 'EM'
    ABRIL_JULIO = 'AJ'
    JULIO_AGOSTO = 'JA'

    TRIMESTRES_USB = (
        (SEPTIEMBRE_DICIEMBRE,'Septiembre - Diciembre'),
        (ENERO_MARZO, 'Enero - Marzo'),
        (ABRIL_JULIO, 'Abril - Julio'),
        (JULIO_AGOSTO, 'Julio - Agosto'),
    )

    periodo   = models.CharField(
        max_length=2,
        choices=TRIMESTRES_USB,
        default=SEPTIEMBRE_DICIEMBRE,
    )
    anyo = models.CharField(max_length=5)

## Representa un trimestre con los datos reales de curso de un usuario particular
# Por ejemplo: fotos del trimestre, notas particulares,...
class TrimestrePlaneado(models.Model):
    trimestre_base_fk = models.ForeignKey(TrimestreBase, on_delete=models.CASCADE)
    planestudio_pert_fk = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE)

## Representa una materia de la misma forma que TrimestreBase representa un trimestre
# Este modelo puede ser referenciado por multiples planes de distintos usuarios
# Por lo que puede usarse para guardar datos generales para todos los usuarios/planes
class MateriaBase(models.Model):
    POSIBLES_NOTAS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    POSIBLES_CREDITOS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=10,primary_key=True)
    creditos = models.CharField(
        max_length=1,
        choices=POSIBLES_CREDITOS,
        default='1',
    )

# Representa una materia con los datos particulares de cuando un usuario la va a cursar o la cursó
class MateriaPlaneada(models.Model):
    materia_base_fk = models.ForeignKey(MateriaBase, on_delete=models.CASCADE)
    trimestre_cursada_fk = models.ForeignKey(TrimestrePlaneado, on_delete=models.CASCADE)
    nota_final = models.CharField(
        max_length=1,
        choices=MateriaBase.POSIBLES_NOTAS,
        default='1',
    )
    esta_retirada = models.BooleanField(default=False)

