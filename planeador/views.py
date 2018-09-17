# coding=utf-8
import ssl
from urllib import request
from urllib.parse import quote
import requests, ssl
import urllib3

from bs4 import BeautifulSoup
from bs4.builder import HTMLTreeBuilder
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from api_misvoti.gdrive.administrar_drive_planes import gdrive_obtener_contenido_plan, gdrive_crear_nuevo_plan
from api_misvoti.models import *
from planeador.busqueda_bd import refinarBusqueda
from planeador.cargar_pensum_desde_ods import cargar_pensum_ods
from planeador.crear_plan_usuario_desde_pensum import llenar_plan_con_pensum_escogido
from planeador.decorators import only_allow_https
from planeador.expediente_dii_com_scraper import get_expediente_page_content
from planeador.forms import CrearNuevoPlanForm, CrearNuevoPlanExpedienteDescargado, DatosAccesoCASForm
from planeador.obtener_datos_plan import obtener_datos_analisis
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser
from planeador.usbldap import obtener_datos_desde_ldap, random_password


@login_required
def index_vista(request):
    """
    Home Vista que solo redirige a la vista ver_plan
    :param request:
    :return:
    """
    context = {"pagename": "home"}

    if not request.user.gdrive_id_json_plan:
        return render(request, 'planeador/page-sin-plan.html', context)

    return redirect('ver_plan')


# Vista para los usuarios no registrados
# def index_vista(request):
#    context = {}
#    if request.user.is_authenticated():
#        return redirect('planes')
#
#    if request.method == "POST":
#        form = AuthenticationForm(data=request.POST)
#        if form.is_valid():
#            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
#            if user is not None:
#                login(request, user)
#                user.forma_acceso = MiVotiUser.INTERNA
#                user.save()
#                return redirect('planes')
#            else:
#                pass
#    else:
#        form = AuthenticationForm()
#
#    context["form"] = form
#    return render(request, 'misvoti/index.html', context)

@login_required()
def crear_plan_vacio_vista(request):
    """
    Vista para crear un plan guiandose por los trimestres del pensum

    :param request:
    :return:
    """
    user = request.user

    try:
        carrera_plan_bd = CarreraUsb.objects.get(codigo=user.codigo_carrera)
    except ObjectDoesNotExist:
        return HttpResponse(status=400)

    try:
        pensum_escogido = Pensum.objects.get(
            carrera=carrera_plan_bd,
            tipo=user.tipo_pensum
        )
    except ObjectDoesNotExist:
        return HttpResponse(status=400)

    dict_nuevo_plan = {
        'id_pensum': pensum_escogido.id,
        'trimestres': [],
    }

    gdrive_file = gdrive_crear_nuevo_plan(user.username, dict_nuevo_plan)
    if gdrive_file:
        user.gdrive_id_json_plan = gdrive_file['id']
        user.save()
    messages.success(request, "¡Creado plan sin trimestres!")
    return redirect('home')


@login_required()
def crear_plan_base_vista(request):
    """
    Vista para crear un plan guiandose por los trimestres del pensum

    :param request:
    :return:
    """
    user = request.user

    try:
        carrera_plan_bd = CarreraUsb.objects.get(codigo=user.codigo_carrera)
    except ObjectDoesNotExist:
        return HttpResponse(status=400)

    try:
        pensum_escogido = Pensum.objects.get(
            carrera=carrera_plan_bd,
            tipo=user.tipo_pensum
        )
    except ObjectDoesNotExist:
        return HttpResponse(status=400)

    dict_nuevo_plan = {
        'id_pensum': pensum_escogido.id,
    }

    anyo_inicio_usu = user.anyo_inicio

    llenar_plan_con_pensum_escogido(dict_nuevo_plan, anyo_inicio_usu)

    gdrive_file = gdrive_crear_nuevo_plan(user.username, dict_nuevo_plan)

    user.gdrive_id_json_plan = gdrive_file['id']
    user.save()

    messages.success(request, "¡Creado plan de acuerdo al pensum de tu carrera!")
    return redirect('home')


@login_required()
@only_allow_https
def crear_plan_desde_expe_url(request):
    """
    Vista para crear un plan accediendo a la página del expediente del usuario
    :param request:
    :return:
    """
    context = {"pagename": "ver_plan"}

    user = request.user

    if request.method == 'POST':

        form = DatosAccesoCASForm(request.POST)
        context["form"] = form

        if form.is_valid():

            try:
                carrera_plan_bd = CarreraUsb.objects.get(codigo=user.codigo_carrera)
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            try:
                pensum_escogido = Pensum.objects.get(
                    carrera=carrera_plan_bd,
                    tipo=user.tipo_pensum
                )
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            dict_nuevo_plan = {
                'id_pensum': pensum_escogido.id,
            }

            usbid = form.cleaned_data['usbid']
            caspassword = form.cleaned_data['password_cas']

            content_page_expediente = get_expediente_page_content(usbid, caspassword)

            if content_page_expediente == False or content_page_expediente is None:
                form.add_error(None, "Error accediendo al expediente. Posibles datos de acceso errones.")
                messages.error(request,'Error accediendo a la página del expediente.')
                return render(request, 'planeador/page-crear-plan-expe-url.html', context)

            if content_page_expediente != '':
                # Parseamos el html
                crear_modelos_desde_resultado_parser(
                    dict_nuevo_plan,
                    parser_html(content_page_expediente),
                )

                gdrive_file = gdrive_crear_nuevo_plan(request.user.username, dict_nuevo_plan)

                request.user.gdrive_id_json_plan = gdrive_file['id']
                request.user.save()

                messages.success(request, "¡Creado plan de acuerdo a tu expediente!")
                return redirect('home')
        else:
            messages.error(request, 'Error en el formulario.')


    else:
        context["form"] = DatosAccesoCASForm(user=request.user)

    return render(request, 'planeador/page-crear-plan-expe-url.html', context)


@only_allow_https
@login_required
def crear_plan_desde_expe_descar(request):
    """
    Vista para crear un plan desde un expediente descargado
    :param request:
    :return:
    """
    context = {"pagename": "ver_plan"}

    user = request.user

    if request.method == 'POST':

        form = CrearNuevoPlanExpedienteDescargado(request.POST, request.FILES)

        context["esta_creado_plan"] = False

        if form.is_valid():

            try:
                carrera_plan_bd = CarreraUsb.objects.get(codigo=user.codigo_carrera)
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            try:
                pensum_escogido = Pensum.objects.get(
                    carrera=carrera_plan_bd,
                    tipo=user.tipo_pensum
                )
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            dict_nuevo_plan = {
                'id_pensum': pensum_escogido.id,
            }

            if form.cleaned_data["archivo_html_expediente"]:
                # Parseamos el html
                crear_modelos_desde_resultado_parser(
                    dict_nuevo_plan,
                    parser_html(request.FILES['archivo_html_expediente']),
                )

            gdrive_file = gdrive_crear_nuevo_plan(request.user.username, dict_nuevo_plan)

            request.user.gdrive_id_json_plan = gdrive_file['id']
            request.user.save()

            messages.success(request, "¡Creado plan de acuerdo a tu archivo de expediente cargado!")
            context["esta_creado_plan"] = True
        else:
            context["errors"] = form.errors

        return JsonResponse(context)

    else:
        context["form"] = CrearNuevoPlanExpedienteDescargado()

    return render(request, 'planeador/page-crear-plan-expe-descar.html', context)


@login_required
@only_allow_https
def plan_modificar_trim(request):
    """
    Vista donde el usuario puede editar su plan de estudios
    :param request:
    :return:
    """
    context = {"pagename": "ver_plan"}

    if not request.user.gdrive_id_json_plan:
        return redirect('home')
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
    context = {"pagename": "ver_plan"}

    if request.user.gdrive_id_json_plan:
        dict_plan = gdrive_obtener_contenido_plan(request.user.gdrive_id_json_plan)

        context["plan"] = dict_plan
        context["datos"] = obtener_datos_analisis(dict_plan)

    return render(request, 'planeador/vista_principal_plan.html', context)


def crear_plan_base_test(request):
    """
    Vista de prueba, ejecutar solo una vez cuando se crea la BD _datos_pensum.sqlite3 por primera vez
    :param request:
    :return:
    """
    cargar_pensum_ods("Ingeniería de Computación", '0800', 'planeador/static/planeador/pensums/pensum_0800_pa_2013.ods')

    return HttpResponse('¡Plan Base Creado!')
