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

urlpatterns = [

    ## Página principal que veran los usuarios no registrados
    url(r'^$',views.index,name="home"),

    ## Home para los usuarios registrados que inicien sesión
    url(r'^home/', views.home, name='myhome'),

    # Pagina para ver los planes
    url(r'^planes/$', views.ver_lista_planes, name='planes'),

    # Pagina para ver un plan en especifico
    url(r'^planes/(?P<nombre_plan>.*)/$', views.ver_plan, name='ver_plan'),
    # Pagina para ver los planes
    url(r'^nuevo_plan/$', views.crear_plan, name='crear_plan'),

    url(r'^eliminar_plan/$', views.eliminar_plan_ajax, name='eliminar_plan_ajax'),
    url(r'^obtener_datos_plan/$', views.obtener_datos_plan, name='obtener_datos_plan_ajax'),
    url(r'^actualizar_plan/$', views.actualizar_plan, name='actualizar_plan'),

    url(r'^__test/$', views.__test, name='__test'),

    url(r'^planes_base',views.ver_planes_base,name='planes_base'),
    url(r'^admin/', admin.site.urls),
]
