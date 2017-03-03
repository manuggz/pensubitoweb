# coding=utf-8
import json

import time
from urllib import quote

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your views here.
from django.urls import reverse

from planeador.decorators import si_no_autenticado_redirec_index
from planeador.forms import CrearNuevoPlanForm
from planeador.models import PlanEstudio, TrimestrePlaneado, MateriaPlaneada, \
    PlanEstudioBase, CarreraUsb, MateriaBase, MiVotiUser
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser
from planeador.usbldap import get_ldap_data, random_key

tiempos_tardo_en_respuesta = []
# Vista para los usuarios no registrados
def index(request):
    context = {}
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        print request.POST
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                user.forma_acceso = MiVotiUser.INTERNA
                user.save()
                return HttpResponseRedirect('/home/')
            else:
                pass
    else:
        form = AuthenticationForm()

    context["form"] = form
    return render(request, 'misvoti/index.html', context)

def logout_view(request):
    forma_acceso_usuario = request.user.forma_acceso
    logout(request)
    if forma_acceso_usuario == MiVotiUser.CAS:
        return redirect("http://secure.dst.usb.ve/logout")
    return redirect('home')
# Home para los usuarios registrados que iniciaron sesion
@login_required
def home(request):
    context = {"myhome_activo": "active"}
    return render(request, 'misvoti/home.html', context)

def __test(request):
    f_raw_plan = open("../../../plan_computacion_2013_pensum_raw")

    salida = ""
    for linea in f_raw_plan.readlines():
        salida += "<p>" + linea + "</p>"
    f_raw_plan.close()

    return HttpResponse(salida)


@login_required
def crear_plan(request):
    context = {"planes_activo": "active"}

    if request.method == 'POST':

        form = CrearNuevoPlanForm(request.POST, request.FILES)
        context["esta_creado_plan"] = False
        if form.is_valid():

            nombre_nuevo_plan = form.cleaned_data["nombre_plan"]
            context["nombre_plan"] = nombre_nuevo_plan
            context["errors"] = {"nombre_plan": [],"carrera_plan":[],'plan_utilizar':[]}
            if PlanEstudio.objects.filter(nombre=nombre_nuevo_plan).exists():
                context["errors"]["nombre_plan"].append("¡Ya existe un plan con ese nombre!")
            else:

                try:
                    carrera_plan_bd = CarreraUsb.objects.get(codigo=form.cleaned_data["carrera_plan"])
                except ObjectDoesNotExist:
                    context["errors"]["carrera_plan"].append("¡La carrera seleccionada no existe!")
                    return JsonResponse(context)

                try:

                    #print form.cleaned_data["plan_utilizar"]
                    plan_base = PlanEstudioBase.objects.get(
                        carrera_fk = carrera_plan_bd,
                        tipo = form.cleaned_data["plan_utilizar"]
                    )
                except ObjectDoesNotExist:
                    context["errors"]["plan_utilizar"].append("¡El plan de estudio seleccionado no existe!")
                    return JsonResponse(context)

                nuevo_plan = PlanEstudio(
                    nombre=nombre_nuevo_plan,
                    usuario_creador_fk=request.user,
                    plan_estudio_base_fk=plan_base
                )
                nuevo_plan.save()

                periodo_inicio_usu = form.cleaned_data['periodo_inicio']
                anyo_inicio_usu = form.cleaned_data['anyo_inicio']

                print "'"+periodo_inicio_usu+"'","'"+anyo_inicio_usu+"'"
                if form.cleaned_data["archivo_html_expediente"]:
                    # Parseamos el html
                    crear_modelos_desde_resultado_parser(
                        parser_html(request.FILES['archivo_html_expediente']),
                        nuevo_plan,
                    )
                else:
                    trimestre_inicial_bd = TrimestrePlaneado(
                        periodo=periodo_inicio_usu,
                        planestudio_pert_fk=nuevo_plan,
                        anyo=anyo_inicio_usu
                    )
                    trimestre_inicial_bd.save()

                context["esta_creado_plan"] = True
        else:
            context["errors"] = form.errors

                    # Redireccionamos a la pagina para modificar el expediente
        return JsonResponse(context)

    else:
        context["form"] = CrearNuevoPlanForm()
    return render(request, 'planeador/crear_plan.html', context)

def login_cas(request):

    ticket = request.GET['ticket']
    if not ticket:
        # Error
        print "Error no ticket"
        return HttpResponseRedirect('/home/')
    try:
        import ssl
        import urllib2
        ssl._create_default_https_context = ssl._create_unverified_context

        url_login_cast = quote(request.build_absolute_uri(reverse('login_cas')),safe='')

        url = "https://secure.dst.usb.ve/validate?ticket="+ ticket + "&service=" + url_login_cast
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
    except Exception as e:
        # Error
        print "Error " ,e
        return HttpResponseRedirect('/home/')

    if the_page[0:2] == "no":
        print the_page
        print "Ticket no valido lul"
        # Error
        return HttpResponseRedirect('/home/')
    else:
        # session.casticket = request.vars.getfirst('ticket')
        data  = the_page.split()
        usbid = data[1]

        try:
            usuario_existente = MiVotiUser.objects.get(carnet = usbid)
        except ObjectDoesNotExist:
            usuario_existente = None

        if usuario_existente:
            if not usuario_existente.estan_cargados_datos_ldap:
                us = get_ldap_data(usbid)
                usuario_existente.first_name = us.get('first_name')
                usuario_existente.last_name  = us.get('last_name')
                usuario_existente.email = us.get('email')
                usuario_existente.cedula = us['cedula']
                usuario_existente.telefono = us['phone']
                usuario_existente.tipo = us['tipo']
                usuario_existente.estan_cargados_datos_ldap = True

            usuario_existente.forma_acceso = MiVotiUser.CAS
            usuario_existente.save()

            login(request, usuario_existente)

        else:
            clave   = random_key()
            us      = get_ldap_data(usbid)
            nuevo_usuario = get_user_model().objects.create_user(usbid, us.get('email'),clave)
            nuevo_usuario.first_name = us.get('first_name')
            nuevo_usuario.last_name = us.get('last_name')
            nuevo_usuario.cedula = us['cedula']
            nuevo_usuario.telefono = us['phone']
            nuevo_usuario.tipo = us['tipo']
            nuevo_usuario.carnet = usbid
            nuevo_usuario.estan_cargados_datos_ldap = True
            nuevo_usuario.forma_acceso = MiVotiUser.CAS
            nuevo_usuario.save()
            login(request, nuevo_usuario)

            if (us['tipo'] == "Pregrado") or (us['tipo'] == "Postgrado"):
                # Si es estudiante insertar en su tabla
                pass
            elif us['tipo'] == "Docente":
                # En caso de ser docente, agregar dpto.
                pass



        # Al finalizar login o registro, redireccionamos a home
    return HttpResponseRedirect('/home/')

@login_required
def ver_plan(request, nombre_plan):
    context = {"planes_activo": "active"}
    plan_estudio_modelo_ref = get_object_or_404(PlanEstudio, usuario_creador_fk=request.user, nombre=nombre_plan)

    context["plan"] = plan_estudio_modelo_ref
    context['periodos'] = [(p[0], p[1]) for p in TrimestrePlaneado.PERIODOS_USB]
    context["anyos"] = [(anyo,anyo) for anyo in xrange(1993,2030)]

    return render(request, 'planeador/ver_plan.html', context)


@login_required
def ver_planes_base(request):

    respuesta = {"planes":[]}

    if request.method == "GET":
        print request.GET["carrera"]

        try:
            carrera_buscada = CarreraUsb.objects.get(codigo=request.GET["carrera"])
        except ObjectDoesNotExist:
            return JsonResponse(respuesta)

        get_nombre_plan = PlanEstudioBase.get_nombre_tipo_plan
        respuesta["planes"] = [ {"codigo":plan_base_bd.pk,
                                 "nombre": get_nombre_plan(plan_base_bd)}
                                for plan_base_bd in PlanEstudioBase.objects.filter(carrera_fk=carrera_buscada)]

    return JsonResponse(respuesta)

@login_required
def eliminar_plan_ajax(request):
    context = {}
    if request.method == "POST":
        context["eliminado"] = True
        try:
            plan_estudio = PlanEstudio.objects.get(nombre=request.POST["nombre_plan"])
            plan_estudio.delete();
            context["nombre"] = plan_estudio.nombre
        except ObjectDoesNotExist:
            context["eliminado"] = False

        return JsonResponse(context)

    return HttpResponseNotFound()


@login_required
def obtener_datos_plan(request):
    context = {}
    if request.method == "GET":

        plan_estudio_modelo_ref = get_object_or_404(PlanEstudio, usuario_creador_fk=request.user,
                                                    nombre=request.GET["nombre_plan"])

        trimestres = TrimestrePlaneado.objects.con_trimestres_ordenados(planestudio_pert_fk=plan_estudio_modelo_ref)

        context["nombre_plan"] = plan_estudio_modelo_ref.nombre
        context["trimestres"] = []

        for trimestre in trimestres:
            trimestre_ctx = {"periodo": trimestre.periodo, "anyo": trimestre.anyo}
            trimestre_ctx["materias"] = []

            for materia in MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre):
                materia_ctx = {
                    "nombre": materia.nombre,
                    "codigo": materia.codigo,
                    "creditos": int(materia.creditos),
                    "nota_final": int(materia.nota_final),
                    "esta_retirada": materia.esta_retirada,
                    "tipo": materia.tipo,
                }
                trimestre_ctx["materias"].append(materia_ctx)

            context["trimestres"].append(trimestre_ctx)
        print context

        return JsonResponse(context)

    return HttpResponseNotFound()

@login_required
def materias_vista(request):
    context = {}

    if request.method == "GET":
        codigo_materia = request.GET.get("codigo","")
        max_length = int(request.GET.get("max_length",-1))
        res_exacto = bool(request.GET.get("es_codigo_exacto",False))

        codigos_agregados = []
        context["materias"] = []
        n_agregados = 0

        if not res_exacto:
            lista_materias_base_bd =MateriaBase.objects.filter(codigo__contains=codigo_materia)
        else:
            lista_materias_base_bd =MateriaBase.objects.filter(codigo=codigo_materia)

        for materia in lista_materias_base_bd:
            materia_ctx = {
                "nombre": materia.nombre,
                "codigo": materia.codigo,
                "creditos": int(materia.creditos),
            }
            context["materias"].append(materia_ctx)
            codigos_agregados.append(materia.codigo)

            n_agregados += 1
            if max_length!= -1 and n_agregados >= max_length :
                return JsonResponse(context)

        if not res_exacto:
            lista_materias_planeadas_bd =MateriaPlaneada.objects.filter(codigo__contains=codigo_materia)
        else:
            lista_materias_planeadas_bd =MateriaPlaneada.objects.filter(codigo=codigo_materia)

        for materia in lista_materias_planeadas_bd:
            if materia.codigo not in codigos_agregados :
                materia_ctx = {
                    "nombre": materia.nombre,
                    "codigo": materia.codigo,
                    "creditos": int(materia.creditos),
                }
                context["materias"].append(materia_ctx)

                n_agregados += 1
                if max_length != -1 and n_agregados >= max_length:
                    return JsonResponse(context)

    return JsonResponse(context)

@login_required
def actualizar_plan(request):
    global tiempos_tardo_en_respuesta
    context = {}

    t_inicial = time.time()

    if request.method == "POST":
        context["actualizado"] = True

        datos_post = json.loads(request.POST["datos"])

        try:
            plan_estudio_modelo_ref = PlanEstudio.objects.get(nombre=datos_post["nombre_plan"])

        except ObjectDoesNotExist:
            context["actualizado"] = False
            return JsonResponse(context)

        trimestres_bd = TrimestrePlaneado.objects.filter(planestudio_pert_fk=plan_estudio_modelo_ref)
        trimestres_bd.delete()


        for trimestre in datos_post["trimestres"]:
            #print "trim:" + str(trimestre)
            trimestre_actualmd = TrimestrePlaneado(
                periodo=trimestre["periodo"],
                planestudio_pert_fk=plan_estudio_modelo_ref,
                anyo=trimestre["anyo"],
            )
            trimestre_actualmd.save()

            for materia in trimestre["materias"]:
                try:
                    materia_base = MateriaBase.objects.get(codigo=materia["codigo"])
                    materia["nombre"] = materia_base.nombre
                    materia["codigo"] = materia_base.codigo
                    materia["creditos"] = materia_base.creditos
                except ObjectDoesNotExist:
                    pass

                materiaplan_nueva = MateriaPlaneada(
                    trimestre_cursada_fk=trimestre_actualmd,
                    nota_final=materia["nota_final"],
                    esta_retirada=materia["esta_retirada"],
                    nombre=materia["nombre"],
                    codigo=materia["codigo"],
                    creditos=materia["creditos"],
                    tipo=materia["tipo"],
                )

                materiaplan_nueva.save()

        tiempos_tardo_en_respuesta.append(time.time() -  t_inicial)
        print("tardo: " + str(tiempos_tardo_en_respuesta[-1]))
        return JsonResponse(context)

    return HttpResponseNotFound()


@login_required
def ver_lista_planes(request):
    context = {"planes_activo": "active"}

    context["planes"] = PlanEstudio.objects.filter(usuario_creador_fk=request.user)

    return render(request, 'planeador/tabla_planes.html', context)
