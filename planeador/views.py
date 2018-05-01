# coding=utf-8
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render,redirect

from api_misvoti.gdrive.administrar_drive_planes import gdrive_obtener_contenido_plan, gdrive_crear_nuevo_plan
from api_misvoti.models import *
from planeador.busqueda_bd import refinarBusqueda
from planeador.cargar_pensum_desde_ods import cargar_pensum_ods
from planeador.crear_plan_usuario_desde_pensum import llenar_plan_con_pensum_escogido
from planeador.forms import CrearNuevoPlanForm
from planeador.obtener_datos_plan import obtener_datos_analisis
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser

@login_required
def index_vista(request):
    """
    Home Vista que solo redirige a la vista ver_plan
    :param request:
    :return:
    """

    return redirect('ver_plan')





# TODO: Mover al Api el proceso por POST
@login_required
def crear_plan_vista(request):
    """
    Vista para crear un plan
    Si recibe un GET muestra un formulario en el cual el usuario ingresará los datos del nuevo plan
    Si recibe un POST crea el plan y regresa un Json diciendo si lo creó

    :param request:
    :return:
    """
    context = {"planes_activo": "active"}

    if request.method == 'POST':

        form = CrearNuevoPlanForm(request.POST, request.FILES)

        context["esta_creado_plan"] = False

        if form.is_valid():

            nombre_nuevo_plan = form.cleaned_data["nombre_plan"]
            context["nombre_plan"] = nombre_nuevo_plan
            context["errors"] = {"nombre_plan": [], "carrera_plan": [], 'plan_utilizar': []}

            try:
                carrera_plan_bd = CarreraUsb.objects.get(codigo=form.cleaned_data["carrera_plan"])
            except ObjectDoesNotExist:
                context["errors"]["carrera_plan"].append("¡La carrera seleccionada no existe!")
                return JsonResponse(context)

            try:
                pensum_escogido = Pensum.objects.get(
                    carrera=carrera_plan_bd,
                    tipo=form.cleaned_data["plan_utilizar"]
                )
            except ObjectDoesNotExist:
                context["errors"]["plan_utilizar"].append("¡El pensum seleccionado no existe!")
                return JsonResponse(context)

            dict_nuevo_plan = {
                'nombre':nombre_nuevo_plan,
                'id_pensum':pensum_escogido.id,
            }

            #periodo_inicio_usu = form.cleaned_data['periodo_inicio']
            periodo_inicio_usu = ''
            anyo_inicio_usu = form.cleaned_data['anyo_inicio']

            if form.cleaned_data["archivo_html_expediente"]:

                # Parseamos el html
                crear_modelos_desde_resultado_parser(
                    dict_nuevo_plan,
                    parser_html(request.FILES['archivo_html_expediente']),
                )
            else:
                if form.cleaned_data['construir_usando_pb']:
                    llenar_plan_con_pensum_escogido(dict_nuevo_plan,periodo_inicio_usu,anyo_inicio_usu)

            gdrive_file = gdrive_crear_nuevo_plan(request.user.username,dict_nuevo_plan)

            request.user.gdrive_id_json_plan = gdrive_file['id']
            request.user.save()

            context["esta_creado_plan"] = True
        else:
            context["errors"] = form.errors

        # Redireccionamos a la pagina para modificar el expediente
        return JsonResponse(context)

    else:
        context["form"] = CrearNuevoPlanForm(user=request.user)

    return render(request, 'planeador/page-crear-plan.html', context)


@login_required
def plan_modificar_trim(request):
    """
    Vista donde el usuario puede editar su plan de estudios
    :param request:
    :return:
    """
    context = {"planes_activo": "active"}

    if not request.user.gdrive_id_json_plan:
        return render(request, 'planeador/page-sin-plan.html', context)
    else:

        # Plan del usuario
        context["plan"] = gdrive_obtener_contenido_plan(request.user.gdrive_id_json_plan)

        # Variable usada para estandarizar el nombre/clave usado para los periodos en el back y front
        context['periodos'] = [(p[0], p[1]) for p in TrimestrePensum.PERIODOS_USB]

        # Variable usada para mostrar un select de años en el front
        context["anyos"] = [(anyo, anyo) for anyo in range(1993, 2030)]

        return render(request, 'planeador/page-modificar-plan.html', context)



## Busca materias segun filtros dados por el usuario
# Regresa un JSON con el resultado
# TODO: MOVER AL API!!
@login_required
def materias_vista(request):
    context = {}

    if request.method == "GET":
        nombre_materia = request.GET.get("nombre", "").lower()
        codigo_materia = request.GET.get("codigo", "").lower()

        max_length = int(request.GET.get("max_length", -1))
        res_exacto = bool(request.GET.get("obte_resultado_exacto", False))

        lista_excluidos = []
        context["materias"] = []

        refinarBusqueda(
            nombre_materia,
            codigo_materia,
            res_exacto,
            max_length,
            (lambda mat_bd: lista_excluidos.count(mat_bd.codigo)),
            (lambda mat_bd: lista_excluidos.append(mat_bd.codigo)),
            MateriaBase.objects.all(),
            context["materias"],
            0
        )

    return JsonResponse(context)


@login_required
def ver_plan_vista_principal(request):
    """
    Muestra una vista con un resumen de los datos del plan creado por el usuario
    :param request:
    :return:
    """
    context = {"planes_activo": "active"}

    if request.user.gdrive_id_json_plan:

        dict_plan = gdrive_obtener_contenido_plan(request.user.gdrive_id_json_plan)

        context["plan"]  = dict_plan
        context["datos"] = obtener_datos_analisis(dict_plan)


    return render(request, 'planeador/vista_principal_plan.html', context)



def crear_plan_base_test(request):
    """
    Vista de prueba, ejecutar solo una vez cuando se crea la BD _datos_pensum.sqlite3 por primera vez
    :param request:
    :return:
    """
    cargar_pensum_ods("Ingeniería de Computación",'0800','planeador/static/planeador/pensums/pensum_0800_pa_2013.ods')

    return HttpResponse('¡Plan Base Creado!')


