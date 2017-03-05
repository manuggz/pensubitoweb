# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models



## Modelo para manejar el usuario del sistema
class MiVotiUser(AbstractUser):
    CAS = 'PA' # Forma de Acceso atraves del CAS
    INTERNA = 'IN' # Forma de acceso a traves del login interno de la página
    FORMAS_ACCESO = ( # Indica las posibles formas de acceso que dispone la página
        (CAS, 'CAS'),
        (INTERNA, 'Log interno'),
    )

    # Indica la forma de acceso usada por el usuario para acceder a su sesión actual
    # Notar que hay issues cuando hay multilples sesiones por  el mismo usuario
    # Es usado para cuando el usuario log out de la página saber de que servicio desconectarlo
    forma_acceso = models.CharField(
        max_length=2,
        choices=FORMAS_ACCESO,
        default=INTERNA,
    )

    # Carnet del usuario
    carnet = models.CharField(max_length=10,null=True)

    # Indica si se han cargados los datos del ldap
    estan_cargados_datos_ldap = models.BooleanField(default=False)

    # Cedula del usuario
    cedula = models.CharField(max_length=12,null=True)

    # Tipo de usuario obtenido del ldap
    tipo = models.CharField(max_length=100)


## Representa una carrera de la USB
class CarreraUsb(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.codigo + " - "  + self.nombre

    def __unicode__(self):
        return self.codigo + " - "  + self.nombre


## Plan de estudio base que un usuario puede utilizar para crear sus planes
# Notar que no se guarda más información referente al plan solo que este existe
# Sus detalles se guardarán en otro lugar
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
        return self.carrera_fk.nombre +" " + self.get_nombre_tipo_plan()

    def __unicode__(self):
        return self.carrera_fk.nombre +" " + self.get_nombre_tipo_plan()


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
        return "Plan - " + self.nombre + " | " + str(self.usuario_creador_fk) + ""

    def __unicode__(self):
        return "Plan - " + self.nombre + " | " + str(self.usuario_creador_fk) + ""


## Manager para los trimestres
class TrimestreManager(models.Manager):
    # Regresa el filtro aplicado a los trimestres ordenados
    def con_trimestres_ordenados(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return sorted(qs)


## Representa un trimestre planeado por el usuario
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

    # Los siguientes metodos son para que se puedan ordenar trimestres usando sorted()

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

    ## Compara dos trimestres
    ## Regresa 0 si ambos trimestres son iguales/tienen el mismo nivel en el orden
    ## -1 si el trimestre self es menor /debe estar ordenado en un menor nivel que other
    ##  1 si el trimestre self es mayor/ debe estar en un nivel más alto que other
    ## Basicamente,
    ## 0  => self = other
    ## -1 => self < other
    ##  1 => self > other
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



## Representa una materia dictada en la USB
## Notar que no está enlazada a ningún plan o usuario
## Contiene datos generales de las materias que serán usados para crear MateriaPlaneada
## Cuando se cargan datos desde un expediente se crean estas materias bases
class MateriaBase(models.Model):
    POSIBLES_CREDITOS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    nombre = models.CharField(max_length=200,null=True)
    codigo = models.CharField(max_length=10,primary_key=True)
    creditos = models.CharField(
        max_length=1,
        choices=POSIBLES_CREDITOS,
        default='1',
    )

    def __str__(self):
        return self.nombre + " - " + self.codigo


    def __unicode__(self):
        return self.nombre + " - " + self.codigo


# Representa una materia con los datos particulares de cuando un usuario la va a cursar o la cursó
# Puede contener datos arbitrarios de un usuario distintos a los almacenados en MateriaBase para la materia
# con el mismo código
class MateriaPlaneada(models.Model):
    POSIBLES_NOTAS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
    POSIBLES_TIPOS = (('RG', 'Regular'), ('EX', 'Extraplan'), ('EL', 'Electiva libre'), ('EA', 'Electiva de Area'))
    trimestre_cursada_fk = models.ForeignKey(TrimestrePlaneado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200,null=True)
    codigo = models.CharField(max_length=10)
    creditos = models.CharField(
        max_length=1,
        choices=MateriaBase.POSIBLES_CREDITOS,
        default='1',
    )
    tipo = models.CharField(
        max_length=2,
        choices=POSIBLES_TIPOS,
        default='RG',
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
