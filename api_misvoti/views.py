# coding=utf-8
import json
import os

from django.apps import apps
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_misvoti.models import MiVotiUser
from api_misvoti.permissions import EsElMismo
from api_misvoti.serializer_plan_estudio import PlanEstudioUsuarioSerializer
from api_misvoti.serializers import UserSerializer


class UserDetail(generics.RetrieveAPIView):
    model = MiVotiUser
    queryset = MiVotiUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [
        permissions.IsAuthenticated, EsElMismo
    ]


class UserList(generics.ListCreateAPIView):
    model = MiVotiUser
    queryset = MiVotiUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAdminUser
    ]


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated, EsElMismo))
def user_plan(request, username):
    """
    Obtiene, Crea o Borra el plan creado por un usuario
    """
    if not request.user.gdrive_id_json_plan:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Obtener el plan
        ruta_local = os.path.join('planes_json_cache', request.user.gdrive_id_json_plan)
        if os.path.exists(ruta_local):

            archivo = open(ruta_local)
            dict_plan = json.loads(archivo.read())
            archivo.close()

        else:
            archivo_plan_json = apps.get_app_config('planeador').g_drive.CreateFile(
                {'id': request.user.gdrive_id_json_plan})
            archivo_plan_json.GetContentFile(ruta_local)

            dict_plan = json.loads(archivo_plan_json.GetContentString())

        return Response(dict_plan)
    elif request.method == 'POST':

        # Crear un nuevo Plan
        serializer = PlanEstudioUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Eliminar el plan
        ruta_local = os.path.join('planes_json_cache', request.user.gdrive_id_json_plan)

        if os.path.exists(ruta_local):
            os.remove(ruta_local)

        archivo_plan_json = apps.get_app_config('planeador').g_drive.CreateFile(
            {'id': request.user.gdrive_id_json_plan})
        archivo_plan_json.Delete()

        request.user.gdrive_id_json_plan = None
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
