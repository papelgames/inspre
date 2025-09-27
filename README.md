
## Funcionalidades del aicrag sistema de gestion


### Variables de entorno

Para que la app funcione debes crear las siguientes variables de entorno:

#### Linux/Mac

    export FLASK_APP="entrypoint"
    export FLASK_ENV="development"
    export APP_SETTINGS_MODULE="config.local"

#### Windows

    set "FLASK_APP=entrypoint"
    set "FLASK_ENV=development"
    set "APP_SETTINGS_MODULE=config.local"
    
> Mi recomendación para las pruebas es que añadas esas variables en el fichero "activate" o "activate.bat"
> si estás usando virtualenv
 
### Instalación de dependencias

En el proyecto se distribuye un fichero (requirements.txt) con todas las dependencias. Para instalarlas
basta con ejectuar:

    pip install -r requirements.txt

## Migraciones de bd
flask db init
flask db migrate -m "Initial database"
flask db upgrade

flask db stamp head solo para sqlite
## Ejecución con el servidor que trae Flask

Una vez que hayas descargado el proyecto, creado las variables de entorno e instalado las dependencias,
puedes arrancar el proyecto ejecutando:

    flask run --host=0.0.0.0 --debug




