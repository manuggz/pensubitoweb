import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def gen_indice_for(context,name_for):

    indice_actual = context.get('i_for_' + name_for,-1) + 1
    context['i_for_' + name_for] = indice_actual
    return indice_actual