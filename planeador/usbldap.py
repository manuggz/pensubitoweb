# -*- coding: utf-8 -*-
import ldap
import string
import random

# Requiere:
# sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev ldap-utils
# pip install ldap

# Los resultados vienen de la forma
# Ejemplo estudiante:
# {'status': ['enabled'], 'studentId': ['1110390'], 'cn': ['Manuel Guillermo Gonzalez Malave'], 'uid': ['11-10390'],
#  'objectClass': ['person', 'USBnetPerson', 'posixAccount', 'top', 'shadowAccount'], 'loginShell': ['/sbin/nologin'],
#  'shadowWarning': ['7'], 'uidNumber': ['30846'], 'shadowMax': ['99999'], 'capability': ['mail', 'gmail'],
#  'career': ['Ingenieria de Computacion'], 'gidNumber': ['1004'], 'google': ['enabled'],
# 'gecos': ['Manuel Guillermo Gonzalez Malave,,---'], 'sn': ['Gonzalez Malave'],
#  'homeDirectory': ['/home/pregrado/11-10390'], 'mail': ['11-10390@usb.ve'],
# 'givenName': ['Manuel Guillermo'], 'personalId': ['22900750']}
#
# Para mayor información descargar un "ldap browser" y conectar a "ldap.usb.ve" de forma Anonima
def obtener_datos_desde_ldap(usbid):

    def obtenerValor(maybeList):
        # Evitar excepcion de index no encontrado
        if type(maybeList)==list and len(maybeList)>0:
            return maybeList[0]
        else:
            return None

    user = {}
    l    = ldap.open("ldap.usb.ve")
    searchScope        = ldap.SCOPE_SUBTREE
    retrieveAttributes = None #Traemos todos los atributos
    baseDN = "ou=People,dc=usb,dc=ve"
    searchFilter = "uid=*"+usbid+"*"
    ldap_result_id = l.search(baseDN,searchScope,searchFilter,retrieveAttributes)
    result_type, consulta = l.result(ldap_result_id, 0)
    datos = consulta[0][1]
    # Extraer datos evitando campos inexistentes
    user['first_name'] = obtenerValor(datos.get('givenName'))
    user['last_name']  = obtenerValor(datos.get('sn'))
    user['email']      = obtenerValor(datos.get('mail'))
    user['cedula']     = obtenerValor(datos.get('personalId'))
    user['phone']      = obtenerValor(datos.get('mobile'))
    user_type          = obtenerValor(datos.get('gidNumber'))

    if user_type == "1000":
        user['tipo'] = "Docente"
        user['dpto'] = obtenerValor(datos.get('department'))
    elif user_type == "1002":
        user['tipo'] = "Empleado"
    elif user_type == "1003":
        user['tipo'] = "Organización"
    elif user_type == "1004":
        user['tipo'] = "Pregrado"
        user['carrera'] = obtenerValor(datos.get('career'))
    elif user_type == "1006":
        user['tipo'] = "Postgrado"
        user['carrera'] = obtenerValor(datos.get('career'))
    elif user_type == "1007":
        user['tipo'] = "Egresado"
    elif user_type == "1008":
        user['tipo'] = "Administrativo"

    return user

def random_password():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(20))