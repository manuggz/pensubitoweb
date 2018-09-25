from api_misvoti.models import RelacionMateriaPensumBase, Pensum


def construir_materia_ctx(materia_bd,pensum_ref):
    materia_ctx = {
        "nombre": materia_bd.nombre.upper() if materia_bd.nombre else '',
        "codigo": materia_bd.codigo.upper() if materia_bd.codigo else '',
        "creditos": int(materia_bd.creditos) if materia_bd.creditos else '',
    }

    if pensum_ref:

        rel_materias_pensum = RelacionMateriaPensumBase.objects.filter(materia_base=materia_bd,carrera=pensum_ref.carrera)

        if rel_materias_pensum.exists():
            materia_ctx.update({
                "tipo": rel_materias_pensum.first().tipo_materia,
            })


    return materia_ctx


def refinarBusqueda(nombre, codigo, pensum_cod,mostrar_resultado_exacto,
                    limite_superior_busqueda,
                    esta_excluido,
                    agregar_lista_exclusion,
                    objetos_all,
                    lista_resultado,
                    n_inicial):
    pensum_ref = None
    if pensum_cod:
        try:
            pensum_ref = Pensum.objects.get(pk=pensum_cod)
        except Pensum.DoesNotExist:
            pass

    if not mostrar_resultado_exacto:
        if codigo:
            objetos_all = objetos_all.filter(codigo__contains=codigo)

        if nombre:
            objetos_all = objetos_all.filter(nombre__contains=nombre)

    else:
        if codigo:
            objetos_all = objetos_all.filter(codigo=codigo)

        if nombre:
            objetos_all = objetos_all.filter(nombre=nombre)

    n_agregados = n_inicial
    for materia_bd in objetos_all:
        if not esta_excluido(materia_bd):
            lista_resultado.append(construir_materia_ctx(materia_bd,pensum_ref))
            agregar_lista_exclusion(materia_bd)
            n_agregados += 1
        if limite_superior_busqueda != -1 and n_agregados >= limite_superior_busqueda:
            return n_agregados

    return n_agregados
