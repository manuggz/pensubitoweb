# coding=utf-8
from rest_framework import permissions
from rest_framework.compat import is_authenticated
from rest_framework.request import Request


class EsCreadorPlanOAdmin(permissions.BasePermission):
    """
    Permiso para solo permitir los creadores de un plan realizar una acción.
    """
    def has_object_permission(self, request, view, obj):
        # Request
        if request.user.is_staff:
            return True

        if hasattr(obj, 'planestudio_pert_fk'):
            return obj.planestudio_pert_fk.usuario_creador_fk == request.user
        elif hasattr(obj, 'usuario_creador_fk'):
            return obj.usuario_creador_fk == request.user
        else:
            raise LookupError("No se encuentra al usuario")


class EsElMismo(permissions.BasePermission):
    """
        Permiso para solo permitir a un admin o al mismo usuario acceder al objeto
    """
    def has_object_permission(self, request, view, obj):
        # Request
        if request.user.is_staff:
            return True

        if hasattr(obj, 'username'):
            return obj.username == request.user.username
        else:
            raise LookupError("No posee username")


