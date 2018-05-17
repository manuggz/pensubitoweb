from django.utils.safestring import mark_safe

from planeador.util import return_json_messages_user


def json_messages(request):
    """
    Context Processor for django templates that only add json messages
    :param request:
    :return:
    """
    return {'json_messages':mark_safe(return_json_messages_user(request))}
