from planeador.models import MateriaPlaneada


def obtener_datos_plan(trimestres):
    suma_nota_cred = 0
    creds_inscri = 0
    creds_ret = 0
    creds_apro = 0
    creds_repro = 0
    creds_cont = 0
    n_retiros = 0
    materias_vistas = {}
    for trimestre in trimestres:
        sum_nota_creds_trimact = 0
        cred_cont_trimact = 0

        for materia in MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre):

            cred_materia = int(materia.creditos)
            nota_final = int(materia.nota_final)

            creds_inscri += cred_materia

            if not materia.esta_retirada:

                if nota_final <= 2:
                    creds_repro += cred_materia
                else:
                    resultados_anteriores = materias_vistas.get(materia.codigo)
                    resultado_eliminar = 0

                    if resultados_anteriores:
                        for resultado in resultados_anteriores:
                            if int(resultado.nota_final) <= 2 and not resultado.esta_retirada:
                                resultado_eliminar = int(resultado.nota_final)

                    if resultado_eliminar != 0:
                        creds_cont -= cred_materia
                        suma_nota_cred -= resultado_eliminar*cred_materia

                    creds_apro += cred_materia

                sum_nota_creds_trimact += nota_final * cred_materia
                cred_cont_trimact += cred_materia

            else:
                creds_ret += cred_materia
                n_retiros += 1

            if not materias_vistas.get(materia.codigo):
                materias_vistas[materia.codigo] = [materia]
            else:
                materias_vistas[materia.codigo].append(materia)

        suma_nota_cred += sum_nota_creds_trimact
        creds_cont += cred_cont_trimact

    respuesta = {
        'indice':0 if creds_cont==0 else  round(suma_nota_cred/float(creds_cont),4),
        'creds_inscri' : creds_inscri,
        'creds_ret':creds_ret,
        'creds_apro':creds_apro,
        'creds_repro':creds_repro,
        'n_trimestres':len(trimestres),
        'n_retiros':n_retiros
    }
    return respuesta