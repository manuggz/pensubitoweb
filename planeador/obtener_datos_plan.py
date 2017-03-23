def obtener_datos_analisis(plan):
    suma_nota_cred = 0
    creds_inscri = 0
    creds_ret = 0
    creds_apro = 0
    creds_repro = 0
    creds_cont = 0
    n_retiros = 0
    materias_vistas = {}
    for trimestre_dict in plan['trimestres']:
        sum_nota_creds_trimact = 0
        cred_cont_trimact = 0

        for materia_dict in trimestre_dict['materias']:

            cred_materia = materia_dict.get('creditos',0)

            nota_final = materia_dict.get('nota_final',0)

            creds_inscri += cred_materia

            if not materia_dict.get('esta_retirada',False):

                if nota_final <= 2:
                    creds_repro += cred_materia
                else:

                    if materia_dict.has_key('codigo'):
                        resultados_anteriores = materias_vistas.get(materia_dict['codigo'])
                        resultado_eliminar = 0

                        if resultados_anteriores:
                            for resultado in resultados_anteriores:
                                if int(resultado.nota_final) <= 2 and not resultado.esta_retirada:
                                    resultado_eliminar = int(resultado.nota_final)

                        if resultado_eliminar != 0:
                            creds_cont -= cred_materia
                            suma_nota_cred -= resultado_eliminar * cred_materia

                    creds_apro += cred_materia

                sum_nota_creds_trimact += nota_final * cred_materia
                cred_cont_trimact += cred_materia

            else:
                creds_ret += cred_materia
                n_retiros += 1

            if materia_dict.has_key('codigo'):
                if not materias_vistas.get(materia_dict['codigo']):
                    materias_vistas[materia_dict['codigo']] = [materia_dict]
                else:
                    materias_vistas[materia_dict['codigo']].append(materia_dict)

        suma_nota_cred += sum_nota_creds_trimact
        creds_cont += cred_cont_trimact

    respuesta = {
        'indice': 0 if creds_cont == 0 else  round(suma_nota_cred / float(creds_cont), 4),
        'creds_inscri': creds_inscri,
        'creds_ret': creds_ret,
        'creds_apro': creds_apro,
        'creds_repro': creds_repro,
        'n_trimestres': len(plan['trimestres']),
        'n_retiros': n_retiros
    }
    return respuesta