# coding=utf-8
from urllib import quote
import ssl
import urllib2
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse

from api_misvoti.models import *
from planeador.busqueda_bd import refinarBusqueda
from planeador.cargar_pensum_desde_ods import cargar_pensum_ods
from planeador.crear_plan_usuario_desde_pensum import llenar_plan_con_pensum_escogido
from planeador.forms import CrearNuevoPlanForm
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser
from planeador.usbldap import obtener_datos_desde_ldap, random_password


# Vista para los usuarios no registrados
def index_vista(request):
    context = {}
    if request.user.is_authenticated():
        return redirect('myhome')

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                user.forma_acceso = MiVotiUser.INTERNA
                user.save()
                return redirect('myhome')
            else:
                pass
    else:
        form = AuthenticationForm()

    context["form"] = form
    return render(request, 'misvoti/index.html', context)


# Vista para deslogear a un usuario
def logout_view(request):
    forma_acceso_usuario = request.user.forma_acceso
    logout(request)
    if forma_acceso_usuario == MiVotiUser.CAS:
        return redirect("http://secure.dst.usb.ve/logout")
    return redirect('home')


# Home para los usuarios registrados que iniciaron sesion
@login_required
def home_vista(request):
    context = {"myhome_activo": "active"}
    return render(request, 'misvoti/home.html', context)


## se encarga de logear al usuario que accede a traves del CAS
## A esta vista se le pasa un link del tipo /login_cas/?ticket=ST-11140-4UfRysbyAPox0Kuwnh93-cas
# No debería llamarse desde otro lugar
def login_cas(request):
    # Obtenemos el ticket del login
    ticket = request.GET['ticket']

    if not ticket:
        # Error se necesita el ticket
        return redirect('home')

    # Obtenemos el carnet del ticket
    try:
        # Creamos un nuevo contexto ssl para que no nos de error de verificaciones
        ssl._create_default_https_context = ssl._create_unverified_context

        # Encodificamos el url de esta vista
        url_login_cast = quote(request.build_absolute_uri(reverse('login_cas')), safe='')

        # Construimos el url al servicio del dst que nos dará el carnet
        url = "https://secure.dst.usb.ve/validate?ticket=" + ticket + "&service=" + url_login_cast
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        contenido_pagina = response.read()
    except urllib2.HTTPError as e:
        # Error en la obtención del carnet
        return HttpResponseRedirect('/home/')

    if contenido_pagina[0:2] == "no":
        # contenido_pagina = no
        # Error en el ticket
        return HttpResponseRedirect('/home/')
    else:
        # contenido_pagina = yes 11-10390

        data = contenido_pagina.split()
        usbid = data[1]

        try:
            usuario_existente = MiVotiUser.objects.get(carnet=usbid)
        except ObjectDoesNotExist:
            usuario_existente = None

        if usuario_existente:
            # if not usuario_existente.estan_cargados_datos_ldap:
            #     us = get_ldap_data(usbid)
            #     usuario_existente.first_name = us.get('first_name')
            #     usuario_existente.last_name  = us.get('last_name')
            #     usuario_existente.email = us.get('email')
            #     usuario_existente.cedula = us['cedula']
            #     usuario_existente.telefono = us['phone']
            #     usuario_existente.tipo = us['tipo']
            #     usuario_existente.estan_cargados_datos_ldap = True

            usuario_existente.forma_acceso = MiVotiUser.CAS
            usuario_existente.save()

            login(request, usuario_existente)

        else:
            clave = random_password()
            us = obtener_datos_desde_ldap(usbid)
            nuevo_usuario = get_user_model().objects.create_user(usbid, us.get('email'), clave)
            nuevo_usuario.first_name = us.get('first_name')
            nuevo_usuario.last_name = us.get('last_name')
            nuevo_usuario.cedula = us['cedula']
            nuevo_usuario.telefono = us['phone']
            nuevo_usuario.tipo = us['tipo']
            nuevo_usuario.carnet = usbid
            # nuevo_usuario.estan_cargados_datos_ldap = True
            nuevo_usuario.forma_acceso = MiVotiUser.CAS
            nuevo_usuario.save()
            login(request, nuevo_usuario)

    # Al finalizar login o registro, redireccionamos a home
    return redirect('myhome')


## Vista para crear un plan
# Si recibe un GET muestra un formulario en el cual el usuario ingresará los datos del nuevo plan
# Si recibe un POST crea el plan y regresa un Json diciendo si lo creó
# TODO: Mover al Api el POST por Ajax
@login_required
def crear_plan_vista(request):
    context = {"planes_activo": "active"}

    if request.method == 'POST':
        form = CrearNuevoPlanForm(request.POST, request.FILES)
        context["esta_creado_plan"] = False

        if form.is_valid():

            print form.cleaned_data['construir_usando_pb']
            nombre_nuevo_plan = form.cleaned_data["nombre_plan"]
            context["nombre_plan"] = nombre_nuevo_plan
            context["errors"] = {"nombre_plan": [], "carrera_plan": [], 'plan_utilizar': []}
            if PlanCreado.objects.filter(nombre=nombre_nuevo_plan).exists():
                context["errors"]["nombre_plan"].append("¡Ya existe un plan con ese nombre!")
            else:
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

                nuevo_plan = PlanCreado(
                    nombre=nombre_nuevo_plan,
                    usuario_creador_fk=request.user,
                    pensum=pensum_escogido
                )
                nuevo_plan.save()

                #periodo_inicio_usu = form.cleaned_data['periodo_inicio']
                periodo_inicio_usu = ''
                anyo_inicio_usu = form.cleaned_data['anyo_inicio']

                if form.cleaned_data["archivo_html_expediente"]:
                    # Parseamos el html
                    crear_modelos_desde_resultado_parser(
                        parser_html(request.FILES['archivo_html_expediente']),
                        nuevo_plan,
                    )
                else:
                    if form.cleaned_data['construir_usando_pb']:
                        llenar_plan_con_pensum_escogido(nuevo_plan,periodo_inicio_usu,anyo_inicio_usu)

                context["esta_creado_plan"] = True
        else:
            context["errors"] = form.errors

        # Redireccionamos a la pagina para modificar el expediente
        return JsonResponse(context)

    else:
        context["form"] = CrearNuevoPlanForm(user=request.user)

    return render(request, 'planeador/crear_plan.html', context)


###
# Muestra los datos de un plan creado por el usuario
# La vista se puede editar
@login_required
def plan_vista(request, nombre_plan):
    context = {"planes_activo": "active"}
    plan_estudio_modelo_ref = get_object_or_404(PlanCreado, usuario_creador_fk=request.user, nombre=nombre_plan)

    context["plan"] = plan_estudio_modelo_ref
    context['periodos'] = [(p[0], p[1]) for p in TrimestrePensum.PERIODOS_USB]
    context["anyos"] = [(anyo, anyo) for anyo in xrange(1993, 2030)]

    return render(request, 'planeador/ver_plan.html', context)


###
# Busca los planes bases que posee el sistema y regresa un JSON
# TODO: Mover al API!!
@login_required
def ver_planes_base(request):
    respuesta = {"planes": []}

    if request.method == "GET":
        try:
            carrera_buscada = CarreraUsb.objects.get(codigo=request.GET["carrera"])
        except ObjectDoesNotExist:
            return JsonResponse(respuesta)

        get_nombre_plan = Pensum.get_nombre_tipo_plan
        respuesta["planes"] = [{"codigo": plan_base_bd.pk,
                                "nombre": get_nombre_plan(plan_base_bd)}
                               for plan_base_bd in Pensum.objects.filter(carrera_fk=carrera_buscada)]

    return JsonResponse(respuesta)

## Busca materias segun filtros dados por el usuario
# Regresa un JSON con el resultado
# TODO: Mover al API!!
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

        n_agregados = refinarBusqueda(
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

        if n_agregados == max_length:
            return JsonResponse(context)

        n_agregados = refinarBusqueda(
            nombre_materia,
            codigo_materia,
            max_length,
            res_exacto,
            (lambda mat_bd: lista_excluidos.count(mat_bd.codigo)),
            (lambda mat_bd: lista_excluidos.append(mat_bd.codigo)),
            MateriaPlaneada.objects.all(),
            context["materias"],
            n_agregados
        )

        if n_agregados == max_length:
            return JsonResponse(context)

    return JsonResponse(context)


## Muestra los planes creados por el usuario
@login_required
def planes_vista(request):
    context = {"planes_activo": "active"}

    context["planes"] = []
    n_planes = 0
    for plan_bd in PlanCreado.objects.filter(usuario_creador_fk=request.user):
        plan_ctx = {'nombre': plan_bd.nombre, 'id': plan_bd.id}
        plan_ctx['datos'] = plan_bd.obtener_datos_analisis()

        context["planes"].append(plan_ctx)
        n_planes += 1

    context["n_planes"] = n_planes

    return render(request, 'planeador/tabla_planes.html', context)



def __test(request):
    cargar_pensum_ods("Ingeniería de Computación",'0800','planeador/static/planeador/pensums/pensum_0800_pa_2013.ods')

    return HttpResponse('¡Testeado!')
