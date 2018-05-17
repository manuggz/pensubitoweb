# Pensubito

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
5. Instalar dependencias YARN

En comandos,

    $ git clone https://github.com/manuggz/pensubitoweb.git
    $ cd pensubitoweb
    $ virtualenv venv --no-site-packages
    [LINUX] $ source venv/bin/activate
    [WINDOW]> venv\Scripts\activate
    $ pip install -r requirements.txt
    $ python manage.py migrate
    $ cd misvoti
    $ yarn

¡Listo! , para correr:

    $ python manage.py runserver

## Pasos siguientes

### Crear una cuenta superusuario

    $ python manage.py createsuperuser

Esta te permitirá acceder a la interfaz de administrador de Django:

    http://127.0.0.1:8000/admin/

y para la Interfaz del Api:

    http://127.0.0.1:8000/api/users/

## Pagina Web en Heroku:
https://misvoti.herokuapp.com/

## Autores
- [Manuel González](https://github.com/manuggz)



heroku addons:destroy heroku-postgresql:hobby-dev
heroku addons:create heroku-postgresql:hobby-dev
heroku run migrate
https://github.com/manuggz/heroku-buildpack-python/