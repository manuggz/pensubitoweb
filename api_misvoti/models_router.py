# coding=utf-8

## Dado el nombre de un modelo dice para cual BD debe ir
def debe_ir_db_datos_pensum(nombre_model):

    if nombre_model.find('.') != -1:
        nombre_model = nombre_model[nombre_model.find('.') + 1:].lower()
    return nombre_model == 'carrerausb' or \
           nombre_model == 'pensum' or \
           nombre_model == 'relacionmateriapensumbase' or \
           nombre_model == 'materiabase' or \
           nombre_model == 'trimestrepensum' or \
           nombre_model == 'relacionmateriascorrequisito' or \
           nombre_model == 'relacionmateriaopcional' or \
           nombre_model == 'relacionmateriaprerrequisito'

## Django Router https://docs.djangoproject.com/en/2.1/topics/db/multi-db/
class ApiModelRouter(object):
    """
     Un Router que se encarga de controlar el destino para los modelos en la aplicación su objetivo
     en particular será de decir que los modelos en debe_ir_db_datos_pensum() se tratarán en la BD datos_pensum
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if debe_ir_db_datos_pensum(model._meta.label):
            return 'datos_pensum'

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """

        if debe_ir_db_datos_pensum(model._meta.label):
            return 'datos_pensum'

        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if db == "datos_pensum":
            return app_label == "api_misvoti" and debe_ir_db_datos_pensum(model_name)
        elif app_label == "api_misvoti" and db == "default":
            return not debe_ir_db_datos_pensum(model_name)
        return None
