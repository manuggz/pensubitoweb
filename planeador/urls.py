# coding=utf-8
"""misvoti URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from planeador import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    ## Página principal que veran los usuarios no registrados
    url(r'^$', views.index_vista, name= 'home'),

    ## Home para los usuarios registrados que inicien sesión
    url(r'^home/', views.home_vista, name= 'myhome'),

    # Pagina para ver los planes
    url(r'^planes/$', views.ver_plan_vista_principal, name='planes'),

    # Pagina para ver un plan en especifico
    url(r'^mi_plan/$', views.plan_vista, name='ver_plan'),

    # Pagina para crear un nuevo plan
    url(r'^crear_plan/$', views.crear_plan_vista, name='crear_plan'),

    # Para probar cualquier cosa
    url(r'^__test/$', views.__test, name='__test'),

    # Para obtener los planes base
    url(r'^planes_base',views.ver_planes_base,name='planes_base'),

    # Para obtener las materias base o planeadas segun un filtro
    url(r'^materias/',views.materias_vista,name='materias'),

    url(
        '^logout/$',
        views.logout_view,
        name='logout',
    ),

    url(r'^login_cas/', views.login_cas, name='login_cas'),

]
