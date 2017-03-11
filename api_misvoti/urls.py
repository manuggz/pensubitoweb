from django.conf.urls import url, include
from rest_framework import routers
from api_misvoti import views
from api_misvoti.views import UserPlanesCreadosList, UserDetail, UserList, PlanesCreadosDetail,PlanesCreadosTriList,TrimestresCreadosDetail, \
    PlanesCreadosList,TrimestresCreadosList

user_urls = [
    #url(r'^planes/(?P<pk>[0-9]+)', PlanesCreadosDetail.as_view(), name='planescreados-detail'),
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/planes/$', UserPlanesCreadosList.as_view(), name='userplan-list'),
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^$', UserList.as_view(), name='user-list')
]

planes_creados = [
    url(r'^(?P<pk>\d+)/trimestres/$', PlanesCreadosTriList.as_view(), name='planescreadostrimes-list'),
    url(r'^(?P<pk>\d+)/$', PlanesCreadosDetail.as_view(), name='planescreados-detail'),
    url(r'^$', PlanesCreadosList.as_view(), name='planescreados-list')
]

trimestres_creados = [
    url(r'^(?P<pk>[0-9]+)/$', TrimestresCreadosDetail.as_view(), name='trimestre-detail'),
    url(r'^$', TrimestresCreadosList.as_view(), name='trimestre-list')
]

urlpatterns = (
    url(r'^users/', include(user_urls)),
    url(r'^planes_creados/', include(planes_creados)),
    url(r'^trimestres_creados/', include(trimestres_creados)),
)
