# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from planeador.decorators import si_no_autenticado_redirec_home
from planeador.forms import CrearNuevoPlanForm
from planeador.models import PlanEstudio, TrimestrePlaneado, TrimestreBase, MateriaPlaneada
from planeador.parserexpedientehtml import parser_html, crear_modelos_desde_resultado_parser


# Vista para los usuarios no registrados
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    return render(request, 'misvoti/index.html', {})

# Home para los usuarios registrados que iniciaron sesion
#@si_no_autenticado_redirec_home
def home(request):
    return render(request, 'misvoti/index.html', {})


def crear_plan(request):
    context = {"actual":"crear_plan"}

    if request.method == 'POST':

        form = CrearNuevoPlanForm(request.POST, request.FILES)
        if form.is_valid():

            context["form"] = form
            nombre_nuevo_plan = form.cleaned_data["nombre_plan"]
            if PlanEstudio.objects.filter(nombre=nombre_nuevo_plan).exists():
                form.add_error(form.nombre_plan,"¡Ya existe un plan con ese nombre!")
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


                # Redireccionamos a la pagina para modificar el expediente
                return HttpResponseRedirect('/planes/' + nombre_nuevo_plan + "/")

    else:
        context["form"] = CrearNuevoPlanForm()
    return render(request, 'planeador/crear_plan.html',context)

def ver_plan(request,nombre_plan):
    context = {"actual":"ver_plan"}
    print nombre_plan

    plan_estudio_modelo_ref = get_object_or_404(PlanEstudio,usuario_creador_fk=request.user,nombre=nombre_plan)

    context["plan"] = plan_estudio_modelo_ref

    trimestres = TrimestrePlaneado.objects.filter(planestudio_pert_fk = plan_estudio_modelo_ref)

    context["trimestres"] = []

    for trimestre in trimestres:

        trimestre_ctx = {"periodo":trimestre.trimestre_base_fk.periodo,"anyo":trimestre.trimestre_base_fk.anyo}
        trimestre_ctx["materias"] = MateriaPlaneada.objects.filter(trimestre_cursada_fk = trimestre.pk)
        context["trimestres"].append(trimestre_ctx)

    return render(request, 'planeador/ver_plan.html',context)

@login_required
def ver_lista_planes(request):

    context = {"actual":"planes"}

    context["planes"] = PlanEstudio.objects.filter(usuario_creador_fk=request.user)

    return render(request, 'planeador/planes.html',context)
