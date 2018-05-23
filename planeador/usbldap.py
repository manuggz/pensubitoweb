# -*- coding: utf-8 -*-
import ldap
import string
import random


# Requiere:
# sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev ldap-utils

# Los resultados vienen de la forma
# Ejemplo estudiante:
# {'uid': [b'11-10390'], 'cn': [b'Manuel Guillermo Gonzalez Malave'],
# 'givenName': [b'Manuel Guillermo'], 'sn': [b'Gonzalez Malave'], 'personalId': [b'22900750'],
# 'objectClass': [b'person', b'USBnetPerson', b'posixAccount', b'top', b'shadowAccount'], 'uidNumber': [b'30846'],
# 'gidNumber': [b'1004'], 'homeDirectory': [b'/home/pregrado/11-10390'], 'loginShell': [b'/sbin/nologin'],
# 'gecos': [b'Manuel Guillermo Gonzalez Malave,,---'], 'shadowMax': [b'99999'], 'shadowWarning': [b'7'],
#  'mail': [b'11-10390@usb.ve'], 'capability': [b'mail', b'gmail'], 'career': [b'Ingenieria de Computacion'],
# 'studentId': [b'1110390'], 'status': [b'enabled'], 'google': [b'enabled']}
#
# Para mayor información descargar un "ldap browser" y conectar a "ldap.usb.ve" de forma Anonima
def obtener_datos_desde_ldap(usbid):
    def obtenerValor(maybeList):
        # Evitar excepcion de index no encontrado
        if type(maybeList) == list and len(maybeList) > 0:
            return maybeList[0].decode('utf-8')
        else:
            return None

    l = ldap.open("ldap.usb.ve")
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None  # Traemos todos los atributos
    baseDN = "ou=People,dc=usb,dc=ve"
    searchFilter = "uid=*" + usbid + "*"
    ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
    result_type, consulta = l.result(ldap_result_id, 0)
    datos = consulta[0][1]
    print("datos",datos)

    # Extraer datos evitando campos inexistentes
    user = {}
    user['first_name'] = obtenerValor(datos.get('givenName'))
    user['last_name'] = obtenerValor(datos.get('sn'))
    user['email'] = obtenerValor(datos.get('mail'))
    user['usbid'] = obtenerValor(datos.get('uid'))
    user['cedula'] = obtenerValor(datos.get('personalId'))
    user['phone'] = obtenerValor(datos.get('mobile'))
    user_type = obtenerValor(datos.get('gidNumber'))
    print('user',user)
    print('user_type',user_type)

    if user_type == "1000":
        user['tipo'] = "Docente"
        user['dpto'] = obtenerValor(datos.get('department'))
    elif user_type == "1002":
        user['tipo'] = "Empleado"
    elif user_type == "1003":
        user['tipo'] = "Organización"
    elif user_type == "1006":
        user['tipo'] = "Postgrado"
        user['carrera'] = obtenerValor(datos.get('career'))
    elif user_type == "1007":
        user['tipo'] = "Egresado"
    elif user_type == "1008":
        user['tipo'] = "Administrativo"
    elif user_type == "1004" or not user_type:
        user['tipo'] = "Pregrado"
        user['carrera'] = obtenerValor(datos.get('career'))

    return user


def random_password():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(20))
