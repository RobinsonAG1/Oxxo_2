import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///oxxodb.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # La clave debe ser estable entre reinicios: si cambia, todas las sesiones
    # abiertas se invalidan y los tokens CSRF dejan de ser validos.
    # En produccion se define la variable de entorno SECRET_KEY.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'oxxo-clave-desarrollo-no-usar-en-produccion')


# Comandos para descargar en instalar todas las librerias offline
# python -m pip download -r requirements.txt -d librerias
# pip install --no-index --find-links=librerias -r requirements.txt
