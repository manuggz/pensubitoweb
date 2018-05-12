from api_misvoti.models import *



def llenar_plan_con_pensum_escogido(dict_nuevo_plan, anyo_inicio):


    orden_periodos = {
        TrimestrePensum.ENERO_MARZO:0,
        TrimestrePensum.ABRIL_JULIO:1,
        TrimestrePensum.JULIO_AGOSTO:2,
        TrimestrePensum.SEPTIEMBRE_DICIEMBRE:3
    }

    trimestres_bases_bd = TrimestrePensum.objects.filter(pensum_id = dict_nuevo_plan['id_pensum']).order_by('indice_orden')

    periodo_actual = ''
    periodo_anterior = ''
    anyo_actual = int(anyo_inicio)

    mat_no_incluir = [relacion_bd.materia_segunda_opcion.id for relacion_bd in RelacionMateriaOpcional.objects.filter(pensum_id = dict_nuevo_plan['id_pensum'])]

    l_trims = []

    for trimestre_base_bd in trimestres_bases_bd:

        periodo_anterior = periodo_actual
        periodo_actual = trimestre_base_bd.periodo

        if periodo_anterior != '' and periodo_actual != '':
            if orden_periodos[periodo_actual] <= orden_periodos[periodo_anterior]:
                anyo_actual += 1

        dict_trim = {
            'periodo':periodo_actual,
            'anyo':anyo_actual,
        }

        l_mats = []

        for relacion_mat_bd in RelacionMateriaPensumBase.objects.filter(pensum_id = dict_nuevo_plan['id_pensum'], trimestre_pensum = trimestre_base_bd):

            if relacion_mat_bd.tipo_materia == RelacionMateriaPensumBase.REGULAR:
                if mat_no_incluir.count(relacion_mat_bd.materia_base.id) == 0:
                    dict_mat = {
                        'nombre': relacion_mat_bd.materia_base.nombre,
                        'codigo': relacion_mat_bd.materia_base.codigo,
                        'creditos': relacion_mat_bd.materia_base.creditos,
                        'horas_teoria':relacion_mat_bd.materia_base.horas_teoria,
                        'horas_practica':relacion_mat_bd.materia_base.horas_practica,
                        'horas_laboratorio':relacion_mat_bd.materia_base.horas_laboratorio,
                        'tipo': relacion_mat_bd.tipo_materia
                    }
                    l_mats.append(dict_mat)
            else:
                dict_mat = {
                    'tipo':relacion_mat_bd.tipo_materia,
                }

                l_mats.append(dict_mat)

        dict_trim['materias'] = l_mats
        l_trims.append(dict_trim)

    dict_nuevo_plan['trimestres'] = l_trims