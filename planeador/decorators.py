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
def si_no_autenticado_redirec_home(func):
    def authenticate_and_call(*args, **kwargs):
        if args[0].user.is_authenticated():
            return func(*args, **kwargs)
        return HttpResponseRedirect('/')

    return authenticate_and_call
