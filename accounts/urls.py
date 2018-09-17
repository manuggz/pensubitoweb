from django.conf.urls import include, url
from . import views
from django.urls import path

urlpatterns = [
    path('login/',views.pensubito_normal_login,name='login'),
    path('logout/', views.logout_view, name='logout' ),
    path('login_cas/', views.login_cas, name='login_cas'),
    path('', include('django.contrib.auth.urls')),
    path('crear/',views.crear_cuenta,name="crear_cuenta"),
    path('perfil/', views.mi_perfil, name="user-my-profile"),
    path('perfil/<username>', views.user_perfil, name="user-profile")
]
