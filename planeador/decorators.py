# coding=utf-8
from django.http import HttpResponseRedirect

## Utilizar los decoradores de esta forma:
#
#@decorador
#def home(request):
#   return render(request, 'index.html', {})
#
#


###
# Decorador para vistas
## Este Decorador comprueba si un usuario ha iniciado sesión
# Si no ha iniciado sesión redirecciona a la página de inicio
# En caso contrario continua con la vista
#
from misvoti import settings


def si_no_autenticado_redirec_index(func):
    def authenticate_and_call(*args, **kwargs):
        if args[0].user.is_authenticated():
            return func(*args, **kwargs)
        return HttpResponseRedirect('/')

    return authenticate_and_call

def only_allow_https(func):
    """
    Decorador para vistas
    Si la request no es para la versión Https de la página redirige a la versión segura
    :param func:
    :return:
    """
    def _only_allow_https(request,*args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            return HttpResponseRedirect(request.get_raw_uri().replace('http', 'https'))

        return func(request,*args, **kwargs)

    return _only_allow_https
