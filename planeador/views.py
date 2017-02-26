# coding=utf-8
import json

import time
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from planeador.decorators import si_no_autenticado_redirec_home
from planeador.forms import CrearNuevoPlanForm
from planeador.models import PlanEstudio, TrimestrePlaneado, TrimestreBase, MateriaPlaneada, MateriaBase
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser

tiempos_tardo_en_respuesta = []
# Vista para los usuarios no registrados
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    return render(request, 'misvoti/index.html', {})


# Home para los usuarios registrados que iniciaron sesion
# @si_no_autenticado_redirec_home
def home(request):
    context = {"myhome_activo": "active"}
    return render(request, 'misvoti/index.html', context)


def crear_plan(request):
    context = {"planes_activo": "active"}

    if request.method == 'POST':

        form = CrearNuevoPlanForm(request.POST, request.FILES)
        context["esta_creado_plan"] = False
        context["errors"] = {"nombre_plan":[]}
        if form.is_valid():

            nombre_nuevo_plan = form.cleaned_data["nombre_plan"]
            context["nombre_plan"] = nombre_nuevo_plan
            if PlanEstudio.objects.filter(nombre=nombre_nuevo_plan).exists():
                context["errors"]["nombre_plan"].append("¡Ya existe un plan con ese nombre!")
            else:

                nuevo_plan = PlanEstudio(
                    nombre=nombre_nuevo_plan,
                    usuario_creador_fk=request.user,
                )
                nuevo_plan.save()

                if form.cleaned_data["archivo_html_expediente"]:
                    # Parseamos el html
                    crear_modelos_desde_resultado_parser(
                        parser_html(request.FILES['archivo_html_expediente']),
                        nuevo_plan,
                    )

                context["esta_creado_plan"] = True
        else:
            context["errors"] = form.errors

                    # Redireccionamos a la pagina para modificar el expediente
        return JsonResponse(context)

    else:
        context["form"] = CrearNuevoPlanForm()
    return render(request, 'planeador/crear_plan.html', context)


def ver_plan(request, nombre_plan):
    context = {"planes_activo": "active"}
    plan_estudio_modelo_ref = get_object_or_404(PlanEstudio, usuario_creador_fk=request.user, nombre=nombre_plan)

    context["plan"] = plan_estudio_modelo_ref

    trimestres = TrimestrePlaneado.objects.con_trimestres_ordenados(planestudio_pert_fk=plan_estudio_modelo_ref)

    context["years"] = range(1996, 2050, 1)
    context["trimestres"] = []

    for trimestre in trimestres:
        trimestre_ctx = {"periodo": trimestre.trimestre_base_fk.periodo, "anyo": trimestre.trimestre_base_fk.anyo}
        trimestre_ctx["materias"] = MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre.pk)
        context["trimestres"].append(trimestre_ctx)

    return render(request, 'planeador/ver_plan.html', context)


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


def obtener_datos_plan(request):
    context = {}
    if request.method == "GET":

        plan_estudio_modelo_ref = get_object_or_404(PlanEstudio, usuario_creador_fk=request.user,
                                                    nombre=request.GET["nombre_plan"])

        trimestres = TrimestrePlaneado.objects.con_trimestres_ordenados(planestudio_pert_fk=plan_estudio_modelo_ref)

        context["nombre_plan"] = plan_estudio_modelo_ref.nombre
        context["trimestres"] = []

        for trimestre in trimestres:
            trimestre_ctx = {"periodo": trimestre.trimestre_base_fk.periodo, "anyo": trimestre.trimestre_base_fk.anyo}
            trimestre_ctx["materias"] = []

            for materia in MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre.pk):
                materia_ctx = {
                    "nombre": materia.materia_base_fk.nombre,
                    "codigo": materia.materia_base_fk.codigo,
                    "creditos": int(materia.materia_base_fk.creditos),
                    "nota_final": int(materia.nota_final),
                    "esta_retirada": materia.esta_retirada,
                }
                trimestre_ctx["materias"].append(materia_ctx)

            context["trimestres"].append(trimestre_ctx)

        return JsonResponse(context)

    return HttpResponseNotFound()


def actualizar_plan(request):
    global tiempos_tardo_en_respuesta
    context = {}

    t_inicial = time.time()

    if request.method == "POST":
        context["actualizado"] = True

        plan_estudio_modelo_ref = None

        datos_post = json.loads(request.POST["datos"])
        try:
            plan_estudio_modelo_ref = PlanEstudio.objects.get(nombre=datos_post["nombre_plan"])

        except ObjectDoesNotExist:
            context["actualizado"] = False
            return JsonResponse(context)

        trimestres_bd = TrimestrePlaneado.objects.filter(planestudio_pert_fk=plan_estudio_modelo_ref)
        trimestres_bd.delete()
        #
        # i = 0
        # while i < len(trimestres_bd):
        #     trimestre_bd = trimestres_bd[i]
        #     periodo_trimestre_bd = trimestre_bd.trimestre_base_fk.periodo
        #     anyo_periodo_trimestre_bd = trimestre_bd.trimestre_base_fk.anyo
        #
        #     j = 0
        #     while j < len(datos_post["trimestres"]):
        #         trimestre_json = datos_post["trimestres"][j]
        #
        #         if trimestre_json["periodo"] == periodo_trimestre_bd and trimestre_json[
        #             "anyo"] == anyo_periodo_trimestre_bd:
        #
        #             materias_trimestre_bd = list(MateriaPlaneada.objects.filter(trimestre_cursada_fk=trimestre_bd))
        #
        #             k = 0
        #             while k < len(materias_trimestre_bd):
        #
        #                 nota_final_materia_bd = materias_trimestre_bd[k].nota_final
        #                 codigo_materia_bd = materias_trimestre_bd[k].materia_base_fk.codigo
        #
        #                 l = 0
        #                 while l < len(trimestre_json["materias"]):
        #
        #                     materia_trimestre_json = trimestre_json["materias"][l]
        #                     nota_final_materia_json = materia_trimestre_json["nota_final"]
        #
        #                     if codigo_materia_bd == materia_trimestre_json["codigo"]:
        #
        #                         if nota_final_materia_bd != nota_final_materia_json:
        #                             materias_trimestre_bd[k].nota_final = nota_final_materia_json
        #                             materias_trimestre_bd[k].save()
        #
        #                         del trimestre_json["materias"][l]
        #                         del materias_trimestre_bd[k]
        #
        #                     else:
        #                         l += 1
        #
        #                 if l == len(trimestre_json["materias"]):
        #                     k += 1
        #
        #             map(Model.delete, materias_trimestre_bd)
        #
        #             for materia_json in trimestre_json["materias"]:
        #                 materiabase_md, is_created = MateriaBase.objects.get_or_create(
        #                     nombre=materia_json["nombre"],
        #                     codigo=materia_json["codigo"],
        #                     creditos=materia_json["creditos"],
        #                 )
        #
        #                 materiaplan_nueva = MateriaPlaneada(
        #                     materia_base_fk=materiabase_md,
        #                     nota_final=materia_json["nota_final"],
        #                     esta_retirada=materia_json["esta_retirada"],
        #                     trimestre_cursada_fk=trimestre_bd,
        #                 )
        #
        #                 materiaplan_nueva.save()
        #
        #             del datos_post["trimestres"][j]
        #             del trimestres_bd[i]
        #             break
        #         else:
        #             j += 1
        #
        #     if j == len(datos_post["trimestres"]):
        #         i += 1
        #
        # map(Model.delete,trimestres_bd)

        for trimestre in datos_post["trimestres"]:
            #print "trim:" + str(trimestre)
            trimestre_basemd, is_created = TrimestreBase.objects.get_or_create(
                periodo=trimestre["periodo"],
                anyo=trimestre["anyo"]
            )

            trimestre_actualmd = TrimestrePlaneado(
                trimestre_base_fk=trimestre_basemd,
                planestudio_pert_fk=plan_estudio_modelo_ref,
            )
            trimestre_actualmd.save()

            for materia in trimestre["materias"]:
                #print "mat:" + str(materia)

                materiabase_md, is_created = MateriaBase.objects.get_or_create(
                    nombre=materia["nombre"],
                    codigo=materia["codigo"],
                    creditos=materia["creditos"],
                )

                materiaplan_nueva = MateriaPlaneada(
                    materia_base_fk=materiabase_md,
                    nota_final=materia["nota_final"],
                    esta_retirada=materia["esta_retirada"],
                    trimestre_cursada_fk=trimestre_actualmd,
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
