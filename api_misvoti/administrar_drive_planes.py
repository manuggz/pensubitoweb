import json
import os
from django.apps import apps
from planeador.gdrive_namespaces import ID_DRIVE_CARPETA_MIS_VOTI



def gdrive_obtener_contenido_plan(gdrive_id):
    """
    :type gdrive_id: Google Drive Id
    :param gdrive_id: Id del archivo en la carpeta del Google Drive
    :return: Diccionario con los datos del plan. {'nombre':string,'trimestres':{...}}
    """

    ruta_local = os.path.join('planes_json_cache', gdrive_id)

    if os.path.exists(ruta_local):

        archivo = open(ruta_local)
        dict_plan = json.loads(archivo.read())
        archivo.close()

    else:
        archivo_plan_json = apps.get_app_config('planeador').g_drive.CreateFile({'id': gdrive_id})

        # Obtiene el contenido del archivo del GD y lo guarda en la ruta: ruta_local, para cachearlo
        archivo_plan_json.GetContentFile(ruta_local)

        # Obtiene el contenido del archivo del GD y lo guarda en la variable dict_plan
        dict_plan = json.loads(archivo_plan_json.GetContentString())

    return dict_plan

def gdrive_crear_nuevo_plan(prefijo_archivo,dict_nuevo_plan):
    """
    Crea un nuevo plan en la carpeta del google drive
    :type prefijo_archivo:string
    :param prefijo_archivo:prefijo para colocarle al archivo creado en el nombre
    :param dict_nuevo_plan: diccionario con los datos del plan a guardar en formato JSON
    :return: GoogleDriveFile que referencia al archivo creado
    """
    gdrive_file = apps.get_app_config('planeador').g_drive.CreateFile(
        {'title': prefijo_archivo + '_plan', 'parents': [
            {
                "kind": "drive#parentReference",
                'id': ID_DRIVE_CARPETA_MIS_VOTI
            }
        ]})
    gdrive_file.SetContentString(json.dumps(dict_nuevo_plan))
    gdrive_file.Upload()  # Upload the file.

    return gdrive_file