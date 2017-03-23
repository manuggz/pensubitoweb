# MisVoti

Un Administrador de planes de estudio.

## Caracteristicas

- Permite la manipulación de trimestres y materias de tu plan.
- Posee planes de estudio base de carreras de la USB.
- Diseño Responsive.
- Te muestra tu Índice Acumulado/Periodo por Trimestre.

## Configurar el entorno

Para tener el entorno configurado siga estos pasos.
1. Crear entorno de ejecución(Entorno virtual)[opcional]
2. Instalar Requerimientos
3. Hacer Migraciones
4. Instalar Migraciones

En comandos,

    $ git clone https://github.com/manuggz/misvoti.git
    $ cd misvoti
    $ virtualenv venv --no-site-packages
    [LINUX] $ source venv/bin/activate
    [WINDOW]> venv\Scripts\activate
    $ pip install -r requirements.txt
    $ python manage.py makemigrations api_misvoti
    $ python manage.py migrate

¡Listo! , para correr:

    $ python manage.py runserver

## A considerar

###Crear una cuenta superusuario para iniciar sesión

    $ python manage.py createsuperuser

O puedes iniciar sesión por CAS

### Crear la BD del plan base de Ing. Computación

Acceder a http://127.0.0.1:8000/crear_plan_base_test/

