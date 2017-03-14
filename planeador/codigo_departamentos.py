# coding=utf-8
# Departamento de Biología y Organismos
import re


CODIGO_DEPARTAMENTO_BIOLOGIA_ORGANISMOS = 'DBO'

DEPARTAMENTO_BIOLOGIA_ORGANISMOS = (
    re.compile('(BOB)|(BC)|(EP)|(GP)'),
    CODIGO_DEPARTAMENTO_BIOLOGIA_ORGANISMOS,
    'Departamento de Biología y Organismos'
)

CODIGO_DEPARTAMENTO_ESTUDIOS_AMBIENTALES = 'DEA'
DEPARTAMENTO_ESTUDIOS_AMBIENTALES = (
    re.compile('EAD'),
    CODIGO_DEPARTAMENTO_ESTUDIOS_AMBIENTALES,
    'Departamento de Estudios Ambientales'
)

CODIGO_DEPARTAMENTO_CIENCIAS_SOCIALES = 'DCS'
DEPARTAMENTO_CIENCIAS_SOCIALES = (
    re.compile('CS.'),
    CODIGO_DEPARTAMENTO_CIENCIAS_SOCIALES,
    'Departamento de Ciencias Sociales'
)

CODIGO_DEPARTAMENTO_CIENCIA_TECNOLOGIA_COMPORTAMIENTO = 'DCT'
DEPARTAMENTO_CIENCIA_TECNOLOGIA_COMPORTAMIENTO = (
    re.compile('CC.'),
    CODIGO_DEPARTAMENTO_CIENCIA_TECNOLOGIA_COMPORTAMIENTO,
    'Departamento de Ciencia y Tecnología del Comportamiento'
)

CODIGO_DEPARTAMENTO_FILOSOFIA = 'DFX'
DEPARTAMENTO_FILOSOFIA = (
    re.compile('FLX'),
    CODIGO_DEPARTAMENTO_FILOSOFIA,
    'Departamento de Filosofia'
)

CODIGO_DEPARTAMENTO_IDIOMAS = 'IDI'
DEPARTAMENTO_IDIOMAS = (
    re.compile('ID'),
    CODIGO_DEPARTAMENTO_IDIOMAS,
    'Departamento de Idiomas'
)

IDIOMA_GENERAL_REG_EXP = re.compile('IDE')


TODOS_DEPARTAMENTOS = (
    DEPARTAMENTO_BIOLOGIA_ORGANISMOS,
    DEPARTAMENTO_ESTUDIOS_AMBIENTALES,
    DEPARTAMENTO_CIENCIAS_SOCIALES,
    DEPARTAMENTO_CIENCIA_TECNOLOGIA_COMPORTAMIENTO,
    DEPARTAMENTO_FILOSOFIA
)

DEPARTAMENTOS_GENERAL = (
    DEPARTAMENTO_BIOLOGIA_ORGANISMOS,
    DEPARTAMENTO_ESTUDIOS_AMBIENTALES,
    DEPARTAMENTO_CIENCIAS_SOCIALES,
    DEPARTAMENTO_CIENCIA_TECNOLOGIA_COMPORTAMIENTO,
    DEPARTAMENTO_FILOSOFIA
)


def codigo_pertenece_departamento(codigo,depart_tri):
    return depart_tri[0].match(codigo) != None

def obtener_departamento_asociado_codigo(codigo):
    for departamento_tri in TODOS_DEPARTAMENTOS:
        if departamento_tri[0].match(codigo):
            return departamento_tri

    return None


def es_idioma_general(codigo):
    return IDIOMA_GENERAL_REG_EXP.match(codigo) != None

def es_general_codigo(codigo):
    for departamento_tri in DEPARTAMENTOS_GENERAL:
        if departamento_tri[0].match(codigo):
            return True

    if es_idioma_general(codigo):
        return True

    return False

