from django.core.exceptions import ObjectDoesNotExist
from odf import opendocument
from odf.namespaces import TABLENS
from odf.table import TableRow, Table

from api_misvoti.models import MateriaBase, RelacionMateriasCorrequisito, CarreraUsb, PlanEstudioBase, \
    RelacionMateriaOpcional, TrimestrePensum
from api_misvoti.models import RelacionMateriaPrerrequisito


def getSheet(opendoc,sheet_name):
    for table_element in opendoc.getElementsByType(Table):
        if table_element.getAttribute(u'name') == sheet_name:
            return table_element
    return None

def cargarMaterias(sheet, plan_base_bd):

    nombres_columnas = []
    leido_nombres_columnas = False

    periodo_actual = ''
    indice_orden_actual = 0
    trimestre_actual_bd_ref = None

    for row_element in sheet.getElementsByType(TableRow):
        columna_actual = 0
        materia_dict = {}

        for table_cell in row_element.childNodes:

            numero_columnas_repetidas = table_cell.attributes.get((TABLENS,u'number-columns-repeated'),1)
            for repetir_i in range(int(numero_columnas_repetidas)):
                for text_node in table_cell.childNodes:
                    if not leido_nombres_columnas:
                        nombres_columnas.append(text_node.childNodes[0].data)
                    else:
                        materia_dict[nombres_columnas[columna_actual]] = text_node.childNodes[0].data
                columna_actual += 1

        if leido_nombres_columnas:
            materia_bd = MateriaBase(
                nombre = materia_dict.get('nombre',''),
                codigo = materia_dict.get('codigo',''),
                creditos= materia_dict.get('creditos',''),
                horas_teoria=int(materia_dict.get('horas teoria',0)),
                horas_practica =int(materia_dict.get('horas practica',0)),
                horas_laboratorio=int(materia_dict.get('horas laboratorio',0)),
                tipo_materia=materia_dict.get('tipo', MateriaBase.REGULAR),
            )

            if periodo_actual != '' and materia_dict.get('periodo','') != periodo_actual:

                indice_orden_actual += 1
                periodo_actual = materia_dict.get('periodo','')

                trimestre_actual_bd_ref = TrimestrePensum(
                    periodo= periodo_actual,
                    indice_orden=indice_orden_actual,
                    planestudio_pert_fk=plan_base_bd
                )

            if materia_dict.get('periodo',''):
                materia_bd.trimestre_plan_pensum = trimestre_actual_bd_ref

            materia_bd.save()

        leido_nombres_columnas = True

def cargarPrerequisitos(sheet,plan_base_bd):
    for row_element in sheet.getElementsByType(TableRow):
        codigo_materia_cursar = row_element.childNodes[0].childNodes[0].childNodes[0].data
        codigo_materia_b = row_element.childNodes[1].childNodes[0].childNodes[0].data

        materia_requerida_bd_ref =  None
        tipo_prerre = RelacionMateriaPrerrequisito.MATERIA_REQUISITO

        try:
            materia_requerida_bd_ref = MateriaBase.objects.get(codigo=codigo_materia_b)
        except ObjectDoesNotExist:
            tipo_prerre = codigo_materia_b


        RelacionMateriaPrerrequisito(
            materia_cursar    = MateriaBase.objects.get(codigo=codigo_materia_cursar),
            materia_requerida = materia_requerida_bd_ref,
            tipo = tipo_prerre,
            pensum=plan_base_bd
        ).save()

def cargarCorrequisitos(sheet,plan_base_bd):
    for row_element in sheet.getElementsByType(TableRow):

        codigo_materia_a = row_element.childNodes[0].childNodes[0].childNodes[0].data
        codigo_materia_b = row_element.childNodes[1].childNodes[0].childNodes[0].data

        RelacionMateriasCorrequisito(
            materia_cursar_junta_a = MateriaBase.objects.get(codigo=codigo_materia_a),
            materia_cursar_junta_b = MateriaBase.objects.get(codigo=codigo_materia_b),
            pensum=plan_base_bd
        ).save()

def cargarOpcionales(sheet,plan_base_bd):
    for row_element in sheet.getElementsByType(TableRow):

        codigo_materia_a = row_element.childNodes[0].childNodes[0].childNodes[0].data
        codigo_materia_b = row_element.childNodes[1].childNodes[0].childNodes[0].data

        try:
            materia_opcional_a_bd_ref = MateriaBase.objects.get(codigo=codigo_materia_a)
        except ObjectDoesNotExist:
            if codigo_materia_a == MateriaBase.ELECTIVA_LIBRE:
                materia_opcional_a_bd_ref = MateriaBase(
                    tipo_materia=MateriaBase.ELECTIVA_LIBRE
                )
                materia_opcional_a_bd_ref.save()
            else:
                raise ReferenceError("No se encuentra el codigo:" + codigo_materia_a)

        try:
            materia_opcional_b_bd_ref = MateriaBase.objects.get(codigo=codigo_materia_b)
        except ObjectDoesNotExist:
            if codigo_materia_b == MateriaBase.ELECTIVA_LIBRE:
                materia_opcional_b_bd_ref = MateriaBase(
                    tipo=MateriaBase.ELECTIVA_LIBRE
                )
                materia_opcional_b_bd_ref.save()
            else:
                raise ReferenceError("No se encuentra el codigo:" + codigo_materia_b)

        RelacionMateriaOpcional(
            materia_opcional_a = materia_opcional_a_bd_ref,
            materia_opcional_b = materia_opcional_b_bd_ref,
            pensum=plan_base_bd
        ).save()

def cargar_pensum_ods(nombre_carrera,codigo_carrera,ruta_pensum_ods):
    doc = opendocument.load(ruta_pensum_ods)

    try:
        carrera_usb = CarreraUsb.objects.get(codigo=codigo_carrera)
        print "Warning! La carrera existia."
    except ObjectDoesNotExist:
        carrera_usb = CarreraUsb(
            nombre=nombre_carrera,
            codigo=codigo_carrera,
        )
        carrera_usb.save()
        print "Info! Creada la carrera."

    try:
        plan_base = PlanEstudioBase.objects.get(
            carrera=carrera_usb,
            tipo=PlanEstudioBase.PASANTIA_LARGA
        )
        print "Warning! El plan ya existia"
    except ObjectDoesNotExist:
        plan_base = PlanEstudioBase(
            carrera=carrera_usb,
            tipo=PlanEstudioBase.PASANTIA_LARGA,
        )
        plan_base.save()
        print "Info! Creado el Plan."

    cargarMaterias(getSheet(doc, 'materias'), plan_base)
    print "Cargadas Materias!"
    cargarPrerequisitos(getSheet(doc, 'prerequisitos'), plan_base)
    print "Cargados Prerrequisitos!"
    cargarCorrequisitos(getSheet(doc, 'correquisitos'), plan_base)
    print "Cargados Correquisitos!"
    cargarOpcionales(getSheet(doc, 'opcionales'), plan_base)
    print "Cargados Opcionales!"
