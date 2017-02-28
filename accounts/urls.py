from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(
        '^login/$',
        auth_views.login,
        {'redirect_authenticated_user': 'misvoti:home'},
        name='login',
    ),
    url(
        '^logout/$',
        auth_views.logout,
        name='logout',
    ),
]
