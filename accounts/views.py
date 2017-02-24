from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views


def crear_cuenta(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/chat/')

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            password=form.cleaned_data['password1'])

            user_autenticado = authenticate(username=user.username, password=form.cleaned_data['password1'])
            login(request, user_autenticado)
            return HttpResponseRedirect('/')

    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


def login_check(request):
    # Todos los usuarios autenticados tienen permiso de chatear
    # Por lo que no hace falta que se autentique con otra cuenta
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    return auth_views.login(request)
