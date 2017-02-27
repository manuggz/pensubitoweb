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
class TrimestreBase(models.Model):
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
        if other is not TrimestrePlaneado: return

        if self.periodo == other.periodo:
            return 0
        else:
            if self.periodo == TrimestreBase.ENERO_MARZO:
                return -1
            elif self.periodo == TrimestreBase.ABRIL_JULIO:
                if other.periodo == TrimestreBase.ENERO_MARZO:
                    return 1
                else:
                    return -1
            elif self.periodo == TrimestreBase.JULIO_AGOSTO:
                if other.periodo == TrimestreBase.SEPTIEMBRE_DICIEMBRE:
                    return -1
                else:
                    return 1
            elif self.periodo == TrimestreBase.SEPTIEMBRE_DICIEMBRE:
                return 1

    def __str__(self):
        return "TrimestreBase(" + self.periodo + ")"

    def __unicode__(self):
        return "TrimestreBase(" + self.periodo + ")"


## Representa un i con los datos reales de curso de un usuario particular
# Por ejemplo: fotos del i, notas particulares,...
class TrimestrePlaneado(models.Model):
    trimestre_base_fk = models.ForeignKey(TrimestreBase, on_delete=models.CASCADE)
    planestudio_pert_fk = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE)
    anyo = models.CharField(max_length=5)
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

        if self.anyo < other.anyo:
            return -1
        elif self.anyo > other.anyo:
            return 1
        else:
            return self.trimestre_base_fk.__cmp__(other.trimestre_base_fk)

    def __str__(self):
        return "TrimestrePlaneado(" + str(self.trimestre_base_fk) + "," + str(self.planestudio_pert_fk) + ")"

    def __unicode__(self):
        return "TrimestrePlaneado(" + str(self.trimestre_base_fk) + "," + str(self.planestudio_pert_fk) + ")"


class DepartamentoUSB(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=5, primary_key=True)

    def __str__(self):
        return "Departamento(" + self.nombre + "," + self.codigo + ")"

    def __unicode__(self):
        return "Departamento(" + self.nombre + "," + self.codigo + ")"


## Representa una materia de la misma forma que TrimestreBase representa un i
# Este modelo puede ser referenciado por multiples planes de distintos usuarios
# Por lo que puede usarse para guardar datos generales para todos los usuarios/planes
class MateriaBase(models.Model):
    POSIBLES_NOTAS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    POSIBLES_CREDITOS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=10, primary_key=True)
    creditos = models.CharField(
        max_length=1,
        choices=POSIBLES_CREDITOS,
        default='1',
    )
    departamento_fk = models.ForeignKey(DepartamentoUSB)

    def __str__(self):
        return self.nombre + " - " + self.codigo

    def __unicode__(self):
        return self.nombre + " - " + self.codigo


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

## Define una materia que se cursara en un trimestre segun un plan
class MateriaPlanBase(models.Model):
    materia_base_cursar_fk = models.ForeignKey(MateriaBase)
    plan_base_fk = models.ForeignKey(PlanEstudioBase)
    trimestre_cursar = models.ForeignKey(TrimestreBase)


### Define un prerequisito en un pensum
### Materia A debe ser aprobada antes de inscribir materia B
class Prerequisito(models.Model):
    materia_a_fk = models.ForeignKey(MateriaBase, related_name="pre_mat_a")
    materia_b_fk = models.ForeignKey(MateriaBase, related_name="pre_mat_b")
    plan_estudio_base_pert_fk = models.ForeignKey(PlanEstudioBase)


## Define un correquisito
## Ambas materias deben inscribirse al mismo tiempo
## Si una de ellas se ha aprobado se puede inscribir la otra sin prelación
class Correquisito(models.Model):
    materia_a_fk = models.ForeignKey(MateriaBase, related_name="corr_mat_a")
    materia_b_fk = models.ForeignKey(MateriaBase, related_name="corr_mat_b")
    plan_estudio_base_pert_fk = models.ForeignKey(PlanEstudioBase)
