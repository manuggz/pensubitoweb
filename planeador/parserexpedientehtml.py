##
# Se ocupa de parsear el expediente
# Primero parsea el html creando estructuras MateriaDatosModelo y TrimestreDatosModelo
# Luego se debe llamar a crear_modelos_desde_resultado_parser el cual crea las estructuras en la BD
# Se hace separado para evitar problemas tales como so ocurre un error en el parser no afecte a la BD
from html.parser import HTMLParser

from django.core.exceptions import ObjectDoesNotExist
from api_misvoti.models import MateriaBase, MiVotiUser, RelacionMateriaPensumBase, TrimestrePensum, Pensum
from planeador.codigo_departamentos import *
from planeador.constants import *


class MateriaDatosModelo:
    def __init__(self):
        self.codigo = ""
        self.nombre = ""
        self.creditos = 0
        self.nota = 0
        self.esta_retirada = False


class TrimestreDatosModelo:
    def __init__(self):
        self.periodo = ""
        self.anyo = ""
        self.materias = []


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.es_nombre_trimestre = False
        self.nombre_trimestre = ""

        self.materia = MateriaDatosModelo()

        self.es_nombre_trimestre = False

        self.es_codigo_materia = False
        self.es_nombre_materia = False
        self.es_creditos_materia = False
        self.es_nota_materia = False
        self.es_observacion_materia = False

        self.esta_parseada_observacion = False

        self.trimestres = []
        self.trimestre_actual = TrimestreDatosModelo()

    def handle_starttag(self, tag, attrs):

        if tag == "td":
            for attr in attrs:
                if attr[0] == "width":
                    if attr[1] == "200":
                        self.es_nombre_trimestre = True
                    elif attr[1] == "50" and not self.materia.codigo:
                        self.es_codigo_materia = True
                    elif attr[1] == "380" and not self.materia.nombre:
                        self.es_nombre_materia = True
                    elif attr[1] == "50" and not self.materia.creditos:
                        self.es_creditos_materia = True
                    elif attr[1] == "45" and not self.materia.nota:
                        self.es_nota_materia = True
                    elif attr[1] == "80" and not self.esta_parseada_observacion:
                        self.es_observacion_materia = True

    def handle_endtag(self, tag):

        if tag == "table" and self.nombre_trimestre:
            self.trimestres.append(self.trimestre_actual)
            self.nombre_trimestre = ""
            self.trimestre_actual = TrimestreDatosModelo()
        elif tag == "tr" and self.esta_parseada_observacion:

            self.esta_parseada_observacion = False

            self.trimestre_actual.materias.append(self.materia)
            self.materia = MateriaDatosModelo()

    def handle_data(self, data):

        if self.es_nombre_trimestre:
            # Crear nuevo Trimestre
            self.nombre_trimestre = data

            if "ENERO" in data:
                per_actual = TrimestrePensum.ENERO_MARZO
            elif "ABRIL" in data:
                per_actual = TrimestrePensum.ABRIL_JULIO
            elif "SEPTIEMBRE" in data:
                per_actual = TrimestrePensum.SEPTIEMBRE_DICIEMBRE
            else:
                per_actual = TrimestrePensum.JULIO_AGOSTO

            self.es_nombre_trimestre = False

            self.trimestre_actual.periodo = per_actual
            self.trimestre_actual.anyo = data[data.rfind("20"):].strip()


        elif self.es_codigo_materia:
            self.materia.codigo = data
            self.es_codigo_materia = False
        elif self.es_nombre_materia:
            #self.materia.nombre = data.strip().decode('ISO-8859-1').title()
            self.materia.nombre = data.strip().title()
            self.es_nombre_materia = False
        elif self.es_creditos_materia:
            self.materia.creditos = data
            self.es_creditos_materia = False
        elif self.es_nota_materia:
            data = data.strip()
            if data == "R":
                self.materia.esta_retirada = True
                self.materia.nota = 1
            else:
                self.materia.nota = data
            self.es_nota_materia = False
        elif self.es_observacion_materia:
            self.es_observacion_materia = False
            self.esta_parseada_observacion = True


def parser_html(archivo_subido):
    parser = MyHTMLParser()
    try:
        # En caso de que archivo_subido sea un archivo
        parser.feed(archivo_subido.read().decode('ISO-8859-1'))
    except AttributeError:
        # Suponemos es un string
        parser.feed(archivo_subido)
    return parser.trimestres


def crear_modelos_desde_resultado_parser(dict_nuevo_plan,resultado_parser):

    l_trims = []

    for trimestre_clase in resultado_parser:

        dict_trim = {
            'periodo':trimestre_clase.periodo,
            'anyo': trimestre_clase.anyo,
        }

        l_mats = []

        for materia_clase in trimestre_clase.materias:

            dict_mat = {
                'nombre':materia_clase.nombre,
                'codigo': materia_clase.codigo,
                'creditos': int(materia_clase.creditos),
                'nota_final' : int(materia_clase.nota),
                'esta_retirada':int(materia_clase.esta_retirada),
                'tipo':REGULAR
            }

            try:
                materia_base = MateriaBase.objects.get(codigo = materia_clase.codigo)
            except ObjectDoesNotExist:
                materia_base = None

            relacion_con_pensum = None

            if materia_base:

                # Se obtiene la instancia del PEnsum para obtener la carrera
                try:
                    pensum_bd = Pensum.objects.get(pk = dict_nuevo_plan['id_pensum'])
                except Pensum.DoesNotExist:
                    pensum_bd = None

                # Intentamos obtener la relacion de la materia con el pensum directamente
                # Ejemplo : CI2525, una materia regular RG para el pensum de computación
                try:
                    relacion_con_pensum = RelacionMateriaPensumBase.objects.get(
                        pensum = pensum_bd,
                        materia_base = materia_base
                    )
                except ObjectDoesNotExist:
                    relacion_con_pensum = None

                if not relacion_con_pensum:
                    # Sino intentamos obtener la relacion de la materia con la carrera
                    # Ejemplo : CE3114, una materia electiva libre para la carrera de computación
                    relacion_con_pensum = RelacionMateriaPensumBase.objects.filter(
                        carrera= pensum_bd.carrera,
                        materia_base = materia_base,
                    )
                    if relacion_con_pensum.exists():
                        relacion_con_pensum = relacion_con_pensum.first()
                    else:
                        # Sino intentamos obtener la relacion de la materia en general
                        # Ejemplo : un general
                        relacion_con_pensum = RelacionMateriaPensumBase.objects.filter(
                            materia_base=materia_base,
                        )
                        if relacion_con_pensum.exists():
                            relacion_con_pensum = relacion_con_pensum.first()
                        else:
                            relacion_con_pensum = None

            if relacion_con_pensum:
                dict_mat['tipo'] = relacion_con_pensum.tipo_materia
            else:
                if es_general_codigo(materia_clase.codigo):
                    dict_mat['tipo'] = GENERAL
                else:
                    dict_mat['tipo'] = EXTRAPLAN

            if materia_base:
                dict_mat.update({
                    'horas_teoria':int(materia_base.horas_teoria),
                    'horas_practica':int(materia_base.horas_practica),
                    'horas_laboratorio':int(materia_base.horas_laboratorio),
                })

            l_mats.append(dict_mat)


        dict_trim['materias'] = l_mats

        l_trims.append(dict_trim)

    dict_nuevo_plan['trimestres'] = l_trims