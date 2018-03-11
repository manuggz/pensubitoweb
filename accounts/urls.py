from django.conf.urls import include, url
from . import views


urlpatterns = [
    url('^login/$',views.login_check),
    url('^logout/$', views.logout_view, name='logout' ),
    url('^', include('django.contrib.auth.urls')),
    url('^crear/$',views.crear_cuenta,name="crear_cuenta"),
    url('^myprofile/$', views.crear_cuenta, name="myprofile")
]
