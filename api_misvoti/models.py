# coding=utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


## Modelo para manejar el usuario del sistema

class MiVotiUser(AbstractUser):

    # Carnet del usuario
    carnet = models.CharField(max_length=10, blank=True)

    # Cedula del usuario
    cedula = models.CharField(max_length=12, blank=True)

    # Id del  Archivo de json en Google Drive
    gdrive_id_json_plan = models.CharField(max_length=50, null=True,blank=True)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"


## Representa una carrera de la USB
class CarreraUsb(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return "{0} {1}".format(self.codigo, self.nombre)

    def __unicode__(self):
        return "{0} {1}".format(self.codigo, self.nombre)

    class Meta:
        verbose_name = "carrera"
        verbose_name_plural = "carreras"
        unique_together = (("nombre", "codigo"),)


## Plan de estudio base que un usuario puede utilizar para crear sus planes
# Notar que no se guarda más información referente al plan solo que este existe
# Sus detalles se guardarán en otro lugar
class Pensum(models.Model):
    PASANTIA_LARGA = 'PA'
    PROYECTO_GRADO = 'PG'
    NO_DEFINIDO = 'ND'

    TIPO_PLAN = (
        (PASANTIA_LARGA, 'Pasantia Larga'),
        (PROYECTO_GRADO, 'Proyecto de grado a dedicación exclusiva'),
        (NO_DEFINIDO, 'No definido')
    )

    carrera = models.ForeignKey(CarreraUsb,on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=2,
        choices=TIPO_PLAN,
        default=NO_DEFINIDO,
    )

    def __str__(self):
        return "{0} {1}".format(self.carrera.nombre, self.get_nombre_tipo_plan())

    def __unicode__(self):
        return "{0} {1}".format(self.carrera.nombre, self.get_nombre_tipo_plan())

    def get_nombre_tipo_plan(self):
        for n, v in Pensum.TIPO_PLAN:
            if n == self.tipo:
                return v

    class Meta:
        verbose_name = "plan de estudio base"
        verbose_name_plural = "planes de estudio bases"
        unique_together = (("carrera", "tipo"),)


## Representa un trimestre planeado por el usuario
class TrimestrePensum(models.Model):
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
    indice_orden = models.IntegerField(default=0)
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE,
                               related_name="trimestres_base")

    def __str__(self):
        # return self.periodo + " " + self.anyo + str(self.planestudio_pert_fk) + ")"
        return "{0} {1} | {2}".format(self.periodo, self.indice_orden, self.planestudio_pert_fk)

    def __unicode__(self):
        # return self.periodo + " " + self.anyo + str(self.planestudio_pert_fk) + ")"
        return "{0} {1} | {2}".format(self.periodo, self.indice_orden, self.planestudio_pert_fk)

    class Meta:
        verbose_name = "trimestre pensum"
        verbose_name_plural = "trimestres pensums"


class RelacionMateriaPensumBase(models.Model):
    GENERAL = 'GE'
    ELECTIVA_LIBRE = 'EL'
    ELECTIVA_DE_AREA = 'EA'
    REGULAR = 'RG'
    EXTRAPLAN = 'EX'
    POSIBLES_TIPOS = (
        (REGULAR, 'Regular'),
        (GENERAL, 'General'),
        (ELECTIVA_LIBRE, 'Electiva libre'),
        (ELECTIVA_DE_AREA, 'Electiva de Area'),
        (EXTRAPLAN, 'Extraplan'),
    )

    tipo_materia = models.CharField(
        max_length=2,
        choices=POSIBLES_TIPOS,
        default=REGULAR,
    )
    trimestre_pensum = models.ForeignKey(TrimestrePensum, on_delete=models.CASCADE, null=True)
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)
    materia_base = models.ForeignKey('MateriaBase', on_delete=models.CASCADE, null=True)


## Representa una materia dictada en la USB
## Notar que no está enlazada a ningún plan o usuario
## Contiene datos generales de las materias que serán usados para crear MateriaPlaneada
## Cuando se cargan datos desde un expediente se crean estas materias bases
class MateriaBase(models.Model):
    nombre = models.CharField(max_length=200, blank=True)
    codigo = models.CharField(max_length=10, blank=True,
                              help_text="Por favor use el siguiente formato: <em>XXX-YYYY</em>.")
    creditos = models.IntegerField(default=3)
    horas_teoria = models.IntegerField(default=0)
    horas_practica = models.IntegerField(default=0)
    horas_laboratorio = models.IntegerField(default=0)

    def __str__(self):
        return "{0} - {1}".format(self.codigo, self.nombre)

    def __unicode__(self):
        return "{0} - {1}".format(self.codigo, self.nombre)

    class Meta:
        verbose_name = "materia base"
        verbose_name_plural = "materias bases"


## Indica una Relación de Prerrequisito donde para inscribir matera_a_cursar se debe cumplir con tipo_prerrequisito
class RelacionMateriaPrerrequisito(models.Model):
    MATERIA_REQUISITO = 'MA'
    PERMISO_COORDINACION_REQUISITO = "PC"
    PRIMER_A_APRO = '1A'
    SEGUNDO_A_APRO = '2A'
    TERCER_A_APRO = '3A'
    CUARTO_A_APRO = '4A'
    QUINTO_A_APRO = '5A'
    materia_cursar = models.ForeignKey(MateriaBase, on_delete=models.CASCADE, related_name="materia_cursar")

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)
    tipo_prerrequisito = models.CharField(
        max_length=2,
        choices=(
            (MATERIA_REQUISITO, 'Materia'),
            (PERMISO_COORDINACION_REQUISITO, 'Permiso de la coordinación'),
            (PRIMER_A_APRO, 'Primer año aprobado'),
            (SEGUNDO_A_APRO, 'Segundo año aprobado'),
            (TERCER_A_APRO, 'Tercer año aprobado'),
            (CUARTO_A_APRO, 'Cuarto año aprobado'),
            (QUINTO_A_APRO, 'Quinto año aprobado'),
        ),
        default=MATERIA_REQUISITO,
    )

    materia_requerida = models.ForeignKey(MateriaBase, on_delete=models.CASCADE, related_name="materias_requeridas",
                                          null=True)

    def __str__(self):
        return "({0}) -> ({1})".format(self.materia_cursar, self.materia_requerida)

    def __unicode__(self):
        return "({0}) -> ({1})".format(self.materia_cursar, self.materia_requerida)

    class Meta:
        verbose_name = "requisito"
        verbose_name_plural = "requisitos"


## Indica que materias A y B son correquisitos por lo que se deben inscribir en el mismo trimestre
class RelacionMateriasCorrequisito(models.Model):
    materia_cursar_junta_a = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,
                                               related_name="materia_cursar_junta_a")
    materia_cursar_junta_b = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,
                                               related_name="materia_cursar_junta_b")
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)

    def __str__(self):
        return "({0}) <-> ({1})".format(self.materia_cursar_junta_a, self.materia_cursar_junta_b)

    def __unicode__(self):
        return "({0}) <-> ({1})".format(self.materia_cursar_junta_a, self.materia_cursar_junta_b)

    class Meta:
        verbose_name = "corequisito"
        verbose_name_plural = "corequisitos"
        unique_together = ('materia_cursar_junta_a', 'materia_cursar_junta_b')


## Indica que entre las materias A y B una de las dos se debe/puede inscribir en un trimestre
## La primera opción es la escogida cuando se crea un pensum por default
class RelacionMateriaOpcional(models.Model):
    materia_primera_opcion = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,
                                               related_name="materia_primera_opcion")
    materia_segunda_opcion = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,
                                               related_name="materia_segunda_opcion")
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)

    def __str__(self):
        return "({0}) o ({1})".format(self.materia_primera_opcion, self.materia_segunda_opcion)

    def __unicode__(self):
        return "({0}) o ({1})".format(self.materia_primera_opcion, self.materia_segunda_opcion)

    class Meta:
        verbose_name = "relacion materia opcional"
        verbose_name_plural = "relaciones de materias opcionales"
        unique_together = ('materia_primera_opcion', 'materia_segunda_opcion')
