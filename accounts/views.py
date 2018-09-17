# coding=utf-8
import codecs
import datetime
import ssl
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.urls import reverse

from accounts.forms import ProfileSettingsForm
from api_misvoti.models import MiVotiUser, CarreraUsb, Pensum
from misvoti import settings
from planeador.decorators import only_allow_https
from planeador.forms import LoginForm, RegisterForm
from planeador.usbldap import random_password, obtener_datos_desde_ldap
from planeador.util import asciify

@login_required
def mi_perfil(request):
    return HttpResponseRedirect(reverse('user-profile', kwargs={'username': request.user.username}))

@login_required
def user_perfil(request,username):

    if username == request.user.username:
        user_profile = request.user
    else:
        return HttpResponse("No se permite visitar perfiles de otros usuarios todavía :(  !")
        try:
            user_profile = MiVotiUser.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponse("Usuario no existe!")

    context = {}
    context['pagename'] = "my_profile"
    context['user_profile'] = user_profile

    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST)
        if form.is_valid():
            user_profile.first_name = form.cleaned_data['name']
            user_profile.last_name = form.cleaned_data['last_name']
            user_profile.email = form.cleaned_data['email']
            user_profile.usbid = form.cleaned_data['usbid']
            user_profile.starting_year = form.cleaned_data['starting_year']

            pensum = form.cleaned_data['pensum']
            try:
                pensum_bd = Pensum.objects.get(pk = pensum)
            except ObjectDoesNotExist:
                pensum_bd = None

            if pensum_bd:
                user_profile.codigo_carrera = pensum_bd.carrera.codigo
                user_profile.tipo_pensum = pensum_bd.tipo

            messages.success(request, "Perfil actualizado!")

            user_profile.save()
        else:
            messages.error(request, "Datos erroneos!")

    else:
        form = ProfileSettingsForm(user=user_profile)

    context['form'] = form

    return render(request, 'accounts/profile.html',context)


def crear_cuenta(request):

    if request.user.is_authenticated:
        return redirect('ver_plan')

    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():

            new_user = MiVotiUser.objects.create_user(
                first_name=form.cleaned_data['name'],
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                usbid=form.cleaned_data['carnet'],
                codigo_carrera=form.cleaned_data['career'],

            )
            if new_user.pk > 0:
                # auth.login(request, user)
                auth.login(request, new_user)
                messages.success(request, "Bienvenido , " + new_user.username + "!")
                return redirect('ver_plan')
            else:
                context['error_form'] = True
    else:
        form = RegisterForm()

    context['form'] = form

    return render(request, 'accounts/signup.html', context)

## se encarga de logear al usuario que accede a traves del CAS
## A esta vista se le pasa un link del tipo /login_cas/?ticket=ST-11140-4UfRysbyAPox0Kuwnh93-cas
# No debería llamarse desde otro lugar
def login_cas(request):
    # Obtenemos el ticket del login
    ticket = request.GET['ticket']

    if not ticket:
        # Error se necesita el ticket
        return redirect('home')

    # Obtenemos el usbid del ticket
    try:
        # Creamos un nuevo contexto ssl para que no nos de error de verificaciones
        ssl._create_default_https_context = ssl._create_unverified_context

        # Encodificamos el url de esta vista
        url_login_cast = quote(request.build_absolute_uri(reverse('login_cas')), safe='')

        # Construimos el url al servicio del dst que nos dará el usbid
        url = "https://secure.dst.usb.ve/validate?ticket=" + ticket + "&service=" + url_login_cast
        req = Request(url)
        response = urlopen(req)
        contenido_pagina = response.read().decode('utf-8')
    except HTTPError as e:
        print(e)
        # Error en la obtención del usbid
        return redirect('home')

    if contenido_pagina[0:2] == "no":
        # contenido_pagina = no
        # Error en el ticket
        return redirect('home')
    else:
        # contenido_pagina = yes 11-10390

        data = contenido_pagina.split()
        usbid = data[1]

        try:
            usuario_existente = MiVotiUser.objects.get(usbid=usbid,estan_cargados_datos_ldap=True)
        except ObjectDoesNotExist:
            usuario_existente = None

        if usuario_existente:
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
            nuevo_usuario.tipo = us.get('tipo')
            nuevo_usuario.estan_cargados_datos_ldap = True
            nuevo_usuario.usbid = us.get('usbid')

            anyo_carnet = int(us.get('usbid')[:2])

            if 0 <= anyo_carnet <= 90:
                nuevo_usuario.anyo_inicio = "{0}{1}".format(20, anyo_carnet)
            else:
                nuevo_usuario.anyo_inicio = "{0}{1}".format(19, anyo_carnet)

            # El nombre de la carrera se guarda con acentos , y del ldap se carga el nombre de la carrera en ascii
            # Antes de comparar si se tiene la carrera regresada por el ldap se debe hacer la conversión de por ejemplo
            # Ingeniería de computación ===> Ingenieria de computacion
            codecs.register_error('asciify', asciify)
            for carrera in CarreraUsb.objects.all():
                if carrera.nombre.encode('ascii', 'asciify').decode('utf-8').lower() == us.get('carrera').lower():
                    nuevo_usuario.codigo_carrera = carrera.codigo

            # nuevo_usuario.estan_cargados_datos_ldap = True
            nuevo_usuario.forma_acceso = MiVotiUser.CAS
            nuevo_usuario.save()
            login(request, nuevo_usuario)

    # Al finalizar login o registro, redireccionamos a home
    return redirect('home')



@only_allow_https
def pensubito_normal_login(request):

    context = {}
    next = request.GET.get('next', '')
    context['next'] = next
    #context['pagename'] = 'login'

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is None:
                context['error_form'] = True
            else:
                auth.login(request, user)
                messages.success(request, "Bienvenido , " + username + "!")
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return redirect('ver_plan')
    else:
        form = LoginForm()

    context['form'] = form
    return render(request, 'accounts/login.html', context)
# Vista para deslogear a un usuario

def logout_view(request):
    """
    Vista para deslogear a un usuario.
    Cierra la conexión del usuario y lo redirige a la vista para los usuarios no autenticados
    :param request:
    :return:
    """
    logout(request)
    return redirect('home')
