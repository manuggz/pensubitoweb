import json
import os
from django.apps import apps

from rest_framework import generics,permissions
from rest_framework import status
from rest_framework.compat import is_authenticated
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from api_misvoti.permissions import EsCreadorPlanOAdmin, EsElMismo
from api_misvoti.serializers import UserSerializer, PlanEstudioSerializer
from api_misvoti.models import MiVotiUser


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

@api_view(['GET', 'PUT', 'DELETE'])
def user_plan(request,username):
    """
    Retrieve, update or delete a plan creado por un usuario
    """
    if not request.user.gdrive_id_json_plan:
        return Response(status=status.HTTP_404_NOT_FOUND)


    if request.method == 'GET':
        ruta_local = os.path.join('planes_json_cache',request.user.gdrive_id_json_plan)
        if os.path.exists(ruta_local):

            archivo = open(ruta_local)
            dict_plan = json.loads(archivo.read())
            archivo.close()

        else:
            archivo_plan_json = apps.get_app_config('planeador').g_drive.CreateFile({'id': request.user.gdrive_id_json_plan})
            archivo_plan_json.GetContentFile(ruta_local)

            dict_plan = json.loads(archivo_plan_json.GetContentString())

        #serializer = SnippetSerializer(snippet)
        return Response(dict_plan)
    elif request.method == 'PUT':
        # serializer = SnippetSerializer(snippet, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pass

    elif request.method == 'DELETE':

        ruta_local = os.path.join('planes_json_cache',request.user.gdrive_id_json_plan)

        if os.path.exists(ruta_local):
            os.remove(ruta_local)

        archivo_plan_json = apps.get_app_config('planeador').g_drive.CreateFile({'id': request.user.gdrive_id_json_plan})
        archivo_plan_json.Delete()

        request.user.gdrive_id_json_plan = None
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
# class PlanesCreadosList(generics.ListCreateAPIView):
#     model = PlanCreado
#     queryset = PlanCreado.objects.all().order_by('usuario_creador_fk')
#     serializer_class = PlanEstudioSerializer
#     permission_classes = [
#         permissions.IsAuthenticated,EsCreadorPlanOAdmin
#     ]
#
#     def get_queryset(self):
#         queryset = super(PlanesCreadosList, self).get_queryset()
#         if not (self.request.user and is_authenticated(self.request.user)) or not self.request.user.is_staff:
#             raise PermissionDenied()
#
#         return queryset
#
#
# class PlanesCreadosDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = PlanCreado.objects.all()
#     serializer_class = PlanEstudioSerializer
#     permission_classes = [
#         permissions.IsAuthenticated,EsCreadorPlanOAdmin
#     ]
#
#
# class PlanesCreadosTriList(generics.ListAPIView):
#     model = TrimestrePlaneado
#     queryset = TrimestrePlaneado.objects.all()
#     serializer_class = TrimestreCreadoSerializer
#     permission_classes = [
#         permissions.IsAuthenticated,EsCreadorPlanOAdmin
#     ]
#
#     def get_queryset(self):
#         queryset = super(PlanesCreadosTriList, self).get_queryset()
#         return queryset.filter(planestudio_pert_fk__pk=self.kwargs.get('pk'))
#
# class TrimestresCreadosList(generics.ListCreateAPIView):
#     model = TrimestrePlaneado
#     queryset = TrimestrePlaneado.objects.all().order_by('planestudio_pert_fk')
#     serializer_class = TrimestreCreadoSerializer
#     permission_classes = [
#         permissions.IsAuthenticated,EsCreadorPlanOAdmin
#     ]
#
#
# class TrimestresCreadosDetail(generics.RetrieveUpdateDestroyAPIView):
#     model = TrimestrePlaneado
#     queryset = TrimestrePlaneado.objects.all()
#     serializer_class = TrimestreCreadoSerializer
#     permission_classes = [
#         permissions.IsAuthenticated,EsCreadorPlanOAdmin
#     ]
