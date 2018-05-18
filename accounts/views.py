# coding=utf-8
import ssl
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.urls import reverse

from api_misvoti.models import MiVotiUser
from misvoti import settings
from planeador.decorators import only_allow_https
from planeador.forms import LoginForm
from planeador.usbldap import random_password, obtener_datos_desde_ldap


def crear_cuenta(request):
    if request.user.is_authenticated:
        return redirect('ver_plan')

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            password=form.cleaned_data['password1'])

            user_autenticado = authenticate(username=user.username, password=form.cleaned_data['password1'])
            login(request, user_autenticado)
            user.forma_acceso = MiVotiUser.INTERNA
            user.save()
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

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
            usuario_existente = MiVotiUser.objects.get(usbid=usbid)
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
            nuevo_usuario.tipo = us.get('tipo')
            nuevo_usuario.usbid = usbid
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
                return HttpResponseRedirect(next)
    else:
        form = LoginForm()

    context['form'] = form
    return render(request, 'registration/login.html', context)
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
