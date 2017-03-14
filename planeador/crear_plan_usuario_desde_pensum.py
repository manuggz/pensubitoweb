from api_misvoti.models import *



def llenar_plan_con_pensum_escogido(plan_creado, periodo_inicio, anyo_inicio):

    orden_periodos = {
        TrimestrePensum.ENERO_MARZO:0,
        TrimestrePensum.ABRIL_JULIO:1,
        TrimestrePensum.JULIO_AGOSTO:2,
        TrimestrePensum.SEPTIEMBRE_DICIEMBRE:3
    }

    trimestres_bases_bd = TrimestrePensum.objects.filter(pensum=plan_creado.pensum).order_by('indice_orden')

    periodo_actual = ''
    periodo_anterior = ''
    anyo_actual = int(anyo_inicio)

    mat_no_incluir = [relacion_bd.materia_segunda_opcion.id for relacion_bd in RelacionMateriaOpcional.objects.filter(pensum = plan_creado.pensum)]

    for trimestre_base_bd in trimestres_bases_bd:

        periodo_anterior = periodo_actual
        periodo_actual = trimestre_base_bd.periodo

        if periodo_anterior != '' and periodo_actual != '':
            if orden_periodos[periodo_actual] <= orden_periodos[periodo_anterior]:
                anyo_actual += 1

        trimestre_plan_actual_bd = TrimestrePlaneado(
            periodo = periodo_actual,
            anyo = anyo_actual,
            planestudio_pert_fk=plan_creado
        )
        trimestre_plan_actual_bd.save()

        for relacion_mat_bd in RelacionMateriaPensumBase.objects.filter(pensum=plan_creado.pensum,trimestre_pensum = trimestre_base_bd):

            if relacion_mat_bd.tipo_materia == RelacionMateriaPensumBase.REGULAR:
                if mat_no_incluir.count(relacion_mat_bd.materia_base.id) == 0:
                    materia_plan_bd = MateriaPlaneada(
                        nombre = relacion_mat_bd.materia_base.nombre,
                        codigo = relacion_mat_bd.materia_base.codigo,
                        creditos= relacion_mat_bd.materia_base.creditos,
                        horas_teoria=relacion_mat_bd.materia_base.horas_teoria,
                        horas_practica =relacion_mat_bd.materia_base.horas_practica,
                        horas_laboratorio=relacion_mat_bd.materia_base.horas_laboratorio,

                        tipo=relacion_mat_bd.tipo_materia,

                        trimestre_cursada_fk = trimestre_plan_actual_bd
                    )
                    materia_plan_bd.save()
            else:
                materia_plan_bd = MateriaPlaneada(
                    tipo=relacion_mat_bd.tipo_materia,
                    trimestre_cursada_fk=trimestre_plan_actual_bd
                )
                materia_plan_bd.save()