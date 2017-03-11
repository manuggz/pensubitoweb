from rest_framework import generics,permissions
from rest_framework.compat import is_authenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from api_misvoti.permissions import EsCreadorPlanOAdmin, EsElMismo
from api_misvoti.serializers import UserSerializer, PlanEstudioSerializer, TrimestreCreadoSerializer, \
    PlanUserEstudioSerializer
from api_misvoti.models import MiVotiUser, PlanCreado, TrimestrePlaneado


class UserDetail(generics.RetrieveAPIView):
    model = MiVotiUser
    queryset = MiVotiUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [
        permissions.IsAuthenticated,EsElMismo
    ]



class UserList(generics.ListCreateAPIView):
    model = MiVotiUser
    queryset = MiVotiUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAdminUser
    ]

class UserPlanesCreadosList(generics.ListAPIView):
    model = PlanCreado
    queryset = PlanCreado.objects.all()
    serializer_class = PlanUserEstudioSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]

    def get_queryset(self):
        queryset = super(UserPlanesCreadosList, self).get_queryset()
        if not (self.request.user and is_authenticated(self.request.user)):
            raise PermissionDenied()

        if self.request.user.username != self.kwargs.get('username') and not self.request.user.is_staff:
            raise PermissionDenied()

        return queryset.filter(usuario_creador_fk__username=self.kwargs.get('username'))

class PlanesCreadosList(generics.ListCreateAPIView):
    model = PlanCreado
    queryset = PlanCreado.objects.all().order_by('usuario_creador_fk')
    serializer_class = PlanEstudioSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]

    def get_queryset(self):
        queryset = super(PlanesCreadosList, self).get_queryset()
        if not (self.request.user and is_authenticated(self.request.user)) or not self.request.user.is_staff:
            raise PermissionDenied()

        return queryset


class PlanesCreadosDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanCreado.objects.all()
    serializer_class = PlanEstudioSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]


class PlanesCreadosTriList(generics.ListAPIView):
    model = TrimestrePlaneado
    queryset = TrimestrePlaneado.objects.all()
    serializer_class = TrimestreCreadoSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]

    def get_queryset(self):
        queryset = super(PlanesCreadosTriList, self).get_queryset()
        return queryset.filter(planestudio_pert_fk__pk=self.kwargs.get('pk'))

class TrimestresCreadosList(generics.ListCreateAPIView):
    model = TrimestrePlaneado
    queryset = TrimestrePlaneado.objects.all().order_by('planestudio_pert_fk')
    serializer_class = TrimestreCreadoSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]


class TrimestresCreadosDetail(generics.RetrieveUpdateDestroyAPIView):
    model = TrimestrePlaneado
    queryset = TrimestrePlaneado.objects.all()
    serializer_class = TrimestreCreadoSerializer
    permission_classes = [
        permissions.IsAuthenticated,EsCreadorPlanOAdmin
    ]
