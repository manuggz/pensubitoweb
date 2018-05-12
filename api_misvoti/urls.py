from django.conf.urls import url, include

from api_misvoti.views import UserDetail, UserList, user_plan

# from api_misvoti.views import UserPlanesCreadosList, UserDetail, UserList, PlanesCreadosDetail,PlanesCreadosTriList,TrimestresCreadosDetail, \
#     PlanesCreadosList,TrimestresCreadosList

user_urls = [
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/plan/$', user_plan, name='userplan-detail'),
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/$', UserDetail.as_view(), name='user-detail'),
    url(r'^$', UserList.as_view(), name='user-list')
]

app_name = "api"
urlpatterns = (
    url(r'^users/', include(user_urls)),
)
