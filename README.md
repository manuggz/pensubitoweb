# MisVoti

Un Administrador de planes de estudio.

## Caracteristicas

- Permite la manipulación de trimestres y materias de tu plan.
- Posee planes de estudio base de carreras de la USB.
- Diseño Responsive.
- Te muestra tu Índice Acumulado/Periodo por Trimestre.

## Configurar el entorno

Para tener el entorno configurado siga estos pasos.
1. Crear entorno de ejecución(Entorno virtual)
2. Instalar Requerimientos
3. Hacer Migraciones
4. Instalar Migraciones

En comandos,

    $ git clone https://github.com/manuggz/misvoti.git
    $ cd misvoti
    $ virtualenv venv --no-site-packages
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ python manage.py makemigrations
    $ python manage.py migrate

¡Listo! , para correr:

    $ python manage.py runserver

## A considerar

- Crear una cuenta superusuario para iniciar sesión



    $ python manage.py createsuperuser

