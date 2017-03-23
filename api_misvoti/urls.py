from django.conf.urls import url, include
from rest_framework import routers
from api_misvoti import views
from api_misvoti.views import UserDetail, UserList#,UserPlanesCreadosList
# from api_misvoti.views import UserPlanesCreadosList, UserDetail, UserList, PlanesCreadosDetail,PlanesCreadosTriList,TrimestresCreadosDetail, \
#     PlanesCreadosList,TrimestresCreadosList

user_urls = [
    #url(r'^(?P<username>[0-9a-zA-Z_-]+)/planes/$', UserPlanesCreadosList.as_view(), name='userplan-list'),
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^$', UserList.as_view(), name='user-list')
]

urlpatterns = (
    url(r'^users/', include(user_urls)),
)
