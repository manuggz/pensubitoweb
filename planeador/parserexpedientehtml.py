from HTMLParser import HTMLParser

from django.core.exceptions import ObjectDoesNotExist

from planeador.models import MateriaBase, TrimestrePlaneado, MateriaPlaneada, MiVotiUser

##
# Se ocupa de parsear el expediente
# Primero parsea el html creando estructuras MateriaDatosModelo y TrimestreDatosModelo
# Luego se debe llamar a crear_modelos_desde_resultado_parser el cual crea las estructuras en la BD
# Se hace separado para evitar problemas tales como so ocurre un error en el parser no afecte a la BD

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
                per_actual = TrimestrePlaneado.ENERO_MARZO
            elif "ABRIL" in data:
                per_actual = TrimestrePlaneado.ABRIL_JULIO
            elif "SEPTIEMBRE" in data:
                per_actual = TrimestrePlaneado.SEPTIEMBRE_DICIEMBRE
            else:
                per_actual = TrimestrePlaneado.JULIO_AGOSTO

            self.es_nombre_trimestre = False

            self.trimestre_actual.periodo = per_actual
            self.trimestre_actual.anyo = data[data.rfind("20"):].strip()


        elif self.es_codigo_materia:
            self.materia.codigo = data
            self.es_codigo_materia = False
        elif self.es_nombre_materia:
            self.materia.nombre = unicode(data.strip(), 'ISO-8859-1')
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
    parser.feed(archivo_subido.read())

    return parser.trimestres


def crear_modelos_desde_resultado_parser(resultado_parser, plan_modelo_ref):
    for trimestre in resultado_parser:
        trimestre_actualmd = TrimestrePlaneado(
            periodo=trimestre.periodo,
            anyo=trimestre.anyo,
            planestudio_pert_fk=plan_modelo_ref,
        )
        trimestre_actualmd.save()

        for materia in trimestre.materias:
            print trimestre.periodo + " " + trimestre.anyo + " " + materia.codigo
            try:
                MateriaBase.objects.get(codigo = materia.codigo)
            except ObjectDoesNotExist:
                MateriaBase(
                    nombre=materia.nombre,
                    codigo=materia.codigo,
                    creditos=materia.creditos,
                ).save()

            materiaplan_nueva = MateriaPlaneada(
                nombre=materia.nombre,
                codigo=materia.codigo,
                creditos=materia.creditos,
                nota_final=materia.nota,
                esta_retirada=materia.esta_retirada,
                trimestre_cursada_fk=trimestre_actualmd,
            )
            materiaplan_nueva.save()

