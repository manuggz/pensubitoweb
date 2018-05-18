from django.conf.urls import include, url
from . import views


urlpatterns = [
    url('^login/$',views.pensubito_normal_login,name='login'),
    url('^logout/$', views.logout_view, name='logout' ),
    url(r'^login_cas/', views.login_cas, name='login_cas'),
    url('^', include('django.contrib.auth.urls')),
    url('^crear/$',views.crear_cuenta,name="crear_cuenta"),
    url('^myprofile/$', views.crear_cuenta, name="myprofile")
]
