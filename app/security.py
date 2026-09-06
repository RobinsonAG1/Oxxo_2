"""Proteccion CSRF minima, sin dependencias externas.

Se apoya en la sesion de Flask: se guarda un token aleatorio por sesion y se
exige en cada peticion que modifique datos (POST/PUT/PATCH/DELETE).
"""
import hmac
import secrets

from flask import abort, request, session

_CAMPO = '_csrf_token'
_METODOS_PROTEGIDOS = {'POST', 'PUT', 'PATCH', 'DELETE'}


def generar_csrf_token():
    """Devuelve el token de la sesion actual, creandolo la primera vez."""
    if _CAMPO not in session:
        session[_CAMPO] = secrets.token_urlsafe(32)
    return session[_CAMPO]


def init_csrf(app):
    """Registra el token en Jinja y la verificacion previa a cada peticion."""
    app.jinja_env.globals['csrf_token'] = generar_csrf_token

    @app.before_request
    def verificar_csrf():
        if request.method not in _METODOS_PROTEGIDOS:
            return None

        esperado = session.get(_CAMPO)
        recibido = request.form.get(_CAMPO) or request.headers.get('X-CSRFToken', '')

        if not esperado or not recibido or not hmac.compare_digest(esperado, recibido):
            abort(400, description='Token de seguridad invalido o ausente. '
                                   'Recarga la pagina e intentalo de nuevo.')
        return None
