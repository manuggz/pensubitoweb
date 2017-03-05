def construir_materia_ctx(materia_bd):
    materia_ctx = {
        "nombre": materia_bd.nombre.upper(),
        "codigo": materia_bd.codigo.upper(),
        "creditos": int(materia_bd.creditos),
    }

    try:
        materia_ctx.update({
            "nota_final": int(materia_bd.nota_final),
            "esta_retirada": materia_bd.esta_retirada,
            "tipo": materia_bd.tipo,
        })
    except AttributeError:
        pass

    return materia_ctx


def refinarBusqueda(nombre, codigo, mostrar_resultado_exacto,
                    limite_superior_busqueda,
                    esta_excluido,
                    agregar_lista_exclusion,
                    objetos_all,
                    lista_resultado,
                    n_inicial):

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
            lista_resultado.append(construir_materia_ctx(materia_bd))
            agregar_lista_exclusion(materia_bd)
            n_agregados += 1
        if limite_superior_busqueda != -1 and n_agregados >= limite_superior_busqueda:
            return n_agregados

    return n_agregados
