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
    carnet = models.CharField(max_length=10,blank=True)

    # Indica si se han cargados los datos del ldap
    estan_cargados_datos_ldap = models.BooleanField(default=False)

    # Cedula del usuario
    cedula = models.CharField(max_length=12,blank=True)

    # Tipo de usuario obtenido del ldap
    tipo = models.CharField(max_length=100,blank=True)

    # Id del  Archivo de json en Google Drive
    gdrive_id_json_plan = models.CharField(max_length=50,null=True,editable=False)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

## Representa una carrera de la USB
class CarreraUsb(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return "{0} {1}".format(self.codigo,self.nombre)

    def __unicode__(self):
        return "{0} {1}".format(self.codigo,self.nombre)

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

    carrera = models.ForeignKey(CarreraUsb)
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
        for n,v in Pensum.TIPO_PLAN:
            if n == self.tipo:
                return v

    class Meta:
        verbose_name = "plan de estudio base"
        verbose_name_plural = "planes de estudio bases"
        unique_together = (("carrera", "tipo"),)

#
# ## Plan de estudio creado por el usuario
# # Un usuario puede crear multiples planes
# class PlanCreado(models.Model):
#     nombre = models.CharField(max_length=200)
#     pensum = models.ForeignKey(Pensum)
#     usuario_creador_fk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="planes_creados")
#
#     def __str__(self):
#         return "Plan: '{0}' - Creador:{1}".format(self.nombre,self.usuario_creador_fk)
#
#     def obtener_datos_analisis(self):
#         suma_nota_cred = 0
#         creds_inscri = 0
#         creds_ret = 0
#         creds_apro = 0
#         creds_repro = 0
#         creds_cont = 0
#         n_retiros = 0
#         materias_vistas = {}
#         trimestres_bd = TrimestrePlaneado.objects.filter(planestudio_pert_fk=self)
#         for trimestre_bd in trimestres_bd:
#             sum_nota_creds_trimact = 0
#             cred_cont_trimact = 0
#
#             for materia in MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre_bd):
#
#                 cred_materia = int(materia.creditos)
#                 nota_final = int(materia.nota_final)
#
#                 creds_inscri += cred_materia
#
#                 if not materia.esta_retirada:
#
#                     if nota_final <= 2:
#                         creds_repro += cred_materia
#                     else:
#                         resultados_anteriores = materias_vistas.get(materia.codigo)
#                         resultado_eliminar = 0
#
#                         if resultados_anteriores:
#                             for resultado in resultados_anteriores:
#                                 if int(resultado.nota_final) <= 2 and not resultado.esta_retirada:
#                                     resultado_eliminar = int(resultado.nota_final)
#
#                         if resultado_eliminar != 0:
#                             creds_cont -= cred_materia
#                             suma_nota_cred -= resultado_eliminar * cred_materia
#
#                         creds_apro += cred_materia
#
#                     sum_nota_creds_trimact += nota_final * cred_materia
#                     cred_cont_trimact += cred_materia
#
#                 else:
#                     creds_ret += cred_materia
#                     n_retiros += 1
#
#                 if not materias_vistas.get(materia.codigo):
#                     materias_vistas[materia.codigo] = [materia]
#                 else:
#                     materias_vistas[materia.codigo].append(materia)
#
#             suma_nota_cred += sum_nota_creds_trimact
#             creds_cont += cred_cont_trimact
#
#         respuesta = {
#             'indice': 0 if creds_cont == 0 else  round(suma_nota_cred / float(creds_cont), 4),
#             'creds_inscri': creds_inscri,
#             'creds_ret': creds_ret,
#             'creds_apro': creds_apro,
#             'creds_repro': creds_repro,
#             'n_trimestres': len(trimestres_bd),
#             'n_retiros': n_retiros
#         }
#         return respuesta
#
#     class Meta:
#         verbose_name = "Plan de estudio creado"
#         verbose_name_plural = "Planes de estudio creados"
#         unique_together = (("nombre", "usuario_creador_fk"),)


## Manager para los trimestres
class TrimestreManager(models.Manager):
    # Regresa el filtro aplicado a los trimestres ordenados
    def con_trimestres_ordenados(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return sorted(qs)

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


## Representa un trimestre planeado por el usuario
# class TrimestrePlaneado(models.Model):
#     periodo = models.CharField(
#         max_length=2,
#         choices=TrimestrePensum.PERIODOS_USB,
#         default=TrimestrePensum.SEPTIEMBRE_DICIEMBRE,
#     )
#     anyo = models.CharField(max_length=5)
#     planestudio_pert_fk = models.ForeignKey(PlanCreado, on_delete=models.CASCADE,related_name="trimestres_planeados")
#     objects = TrimestreManager()

    ## Compara dos trimestres
    ## Regresa 0 si ambos trimestres son iguales/tienen el mismo nivel en el orden
    ## -1 si el trimestre self es menor /debe estar ordenado en un menor nivel que other
    ##  1 si el trimestre self es mayor/ debe estar en un nivel más alto que other
    ## Basicamente,
    ## 0  => self = other
    ## -1 => self < other
    ##  1 => self > other
    # def __cmp__(self, other):
    #     if not isinstance(other, TrimestrePlaneado): return
    #
    #     if int(self.anyo) < int(other.anyo):
    #         return -1
    #     elif int(self.anyo) > int(other.anyo):
    #         return 1
    #     else:
    #         if self.periodo == other.periodo:
    #             return 0
    #         else:
    #             if self.periodo == TrimestrePlaneado.ENERO_MARZO:
    #                 return -1
    #             elif self.periodo == TrimestrePlaneado.ABRIL_JULIO:
    #                 if other.periodo == TrimestrePlaneado.ENERO_MARZO:
    #                     return 1
    #                 else:
    #                     return -1
    #             elif self.periodo == TrimestrePlaneado.JULIO_AGOSTO:
    #                 if other.periodo == TrimestrePlaneado.SEPTIEMBRE_DICIEMBRE:
    #                     return -1
    #                 else:
    #                     return 1
    #             elif self.periodo == TrimestrePlaneado.SEPTIEMBRE_DICIEMBRE:
    #                 return 1
    #
    # def __str__(self):
    #     #return self.periodo + " " + self.anyo + str(self.planestudio_pert_fk) + ")"
    #     return "{0} {1} | {2}".format(self.periodo,self.anyo,self.planestudio_pert_fk)
    #
    # class Meta:
    #     verbose_name = "trimestre creado"
    #     verbose_name_plural = "trimestres creados"

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
    trimestre_pensum = models.ForeignKey(TrimestrePensum, on_delete=models.CASCADE,null=True)
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)
    materia_base = models.ForeignKey('MateriaBase', on_delete=models.CASCADE, null=True)


## Representa una materia dictada en la USB
## Notar que no está enlazada a ningún plan o usuario
## Contiene datos generales de las materias que serán usados para crear MateriaPlaneada
## Cuando se cargan datos desde un expediente se crean estas materias bases
class MateriaBase(models.Model):

    nombre = models.CharField(max_length=200,blank=True)
    codigo = models.CharField(max_length=10,blank=True,help_text="Por favor use el siguiente formato: <em>XXX-YYYY</em>.")
    creditos = models.IntegerField(default=3)
    horas_teoria = models.IntegerField(default=0)
    horas_practica = models.IntegerField(default=0)
    horas_laboratorio = models.IntegerField(default=0)

    def __str__(self):
        return "{0} - {1}({2})".format(self.codigo,self.nombre,self.tipo_materia)
    def __unicode__(self):
        return "{0} - {1}({2})".format(self.codigo,self.nombre,self.tipo_materia)

    class Meta:
        verbose_name = "materia base"
        verbose_name_plural = "materias bases"


# Representa una materia con los datos particulares de cuando un usuario la va a cursar o la cursó
# Puede contener datos arbitrarios de un usuario distintos a los almacenados en MateriaBase para la materia
# con el mismo código
# class MateriaPlaneada(models.Model):
#     POSIBLES_NOTAS = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))
#     trimestre_cursada_fk = models.ForeignKey(TrimestrePlaneado, on_delete=models.CASCADE,related_name="materias_planeadas")
#     nombre = models.CharField(max_length=200,blank=True)
#     codigo = models.CharField(max_length=10,blank=True,help_text="Por favor use el siguiente formato: <em>XXX-YYYY</em>.")
#     creditos = models.IntegerField(default=3)
#     tipo = models.CharField(
#         max_length=2,
#         choices=RelacionMateriaPensumBase.POSIBLES_TIPOS,
#         default=RelacionMateriaPensumBase.REGULAR,
#     )
#     nota_final = models.IntegerField(default=0)
#     horas_teoria = models.IntegerField(default=0)
#     horas_practica = models.IntegerField(default=0)
#     horas_laboratorio = models.IntegerField(default=0)
#
#     esta_retirada = models.BooleanField(default=False)
#
#
#     def __str__(self):
#         return "{0} - {1} | {2}".format(self.codigo,self.nombre,self.trimestre_cursada_fk)
#
#     class Meta:
#         verbose_name = "materia creada"
#         verbose_name_plural = "materias creadas"


class RelacionMateriaPrerrequisito(models.Model):
    MATERIA_REQUISITO = 'MA'
    PERMISO_COORDINACION_REQUISITO = "PC"
    PRIMER_A_APRO = '1A'
    SEGUNDO_A_APRO= '2A'
    TERCER_A_APRO = '3A'
    CUARTO_A_APRO = '4A'
    QUINTO_A_APRO = '5A'
    materia_cursar = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materia_cursar")

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)
    tipo_prerrequisito = models.CharField(
        max_length=2,
        choices=(
            (MATERIA_REQUISITO,'Materia'),
            (PERMISO_COORDINACION_REQUISITO, 'Permiso de la coordinación'),
            (PRIMER_A_APRO, 'Primer año aprobado'),
            (SEGUNDO_A_APRO,'Segundo año aprobado'),
            (TERCER_A_APRO, 'Tercer año aprobado'),
            (CUARTO_A_APRO, 'Cuarto año aprobado'),
            (QUINTO_A_APRO, 'Quinto año aprobado'),
        ),
        default=MATERIA_REQUISITO,
    )

    materia_requerida = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materias_requeridas",null=True)

    def __str__(self):
        return "({0}) -> ({1})".format(self.materia_cursar,self.materia_requerida)

    def __unicode__(self):
        return "({0}) -> ({1})".format(self.materia_cursar,self.materia_requerida)

    class Meta:
        verbose_name = "requisito"
        verbose_name_plural = "requisitos"

class RelacionMateriasCorrequisito(models.Model):
    materia_cursar_junta_a = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materia_cursar_junta_a")
    materia_cursar_junta_b = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materia_cursar_junta_b")
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)

    def __str__(self):
        return "({0}) <-> ({1})".format(self.materia_cursar_junta_a,self.materia_cursar_junta_b)
    def __unicode__(self):
        return "({0}) <-> ({1})".format(self.materia_cursar_junta_a,self.materia_cursar_junta_b)

    class Meta:
        verbose_name = "corequisito"
        verbose_name_plural = "corequisitos"
        unique_together = ('materia_cursar_junta_a','materia_cursar_junta_b')

class RelacionMateriaOpcional(models.Model):
    materia_primera_opcion = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materia_primera_opcion")
    materia_segunda_opcion = models.ForeignKey(MateriaBase, on_delete=models.CASCADE,related_name="materia_segunda_opcion")
    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE)

    def __str__(self):
        return "({0}) o ({1})".format(self.materia_primera_opcion,self.materia_segunda_opcion)
    def __unicode__(self):
        return "({0}) o ({1})".format(self.materia_primera_opcion,self.materia_segunda_opcion)

    class Meta:
        verbose_name = "relacion materia opcional"
        verbose_name_plural = "relaciones de materias opcionales"
        unique_together = ('materia_primera_opcion','materia_segunda_opcion')

