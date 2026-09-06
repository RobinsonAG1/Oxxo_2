"""Validaciones de formularios del panel de administracion.

Cada funcion devuelve la tupla (valor_limpio, error). El error es None cuando
el dato es valido, o un mensaje listo para mostrar con flash().
"""


def texto(valor, campo, maximo, obligatorio=True):
    """Limpia una cadena y comprueba obligatoriedad y longitud maxima."""
    valor = (valor or '').strip()
    if not valor:
        if obligatorio:
            return '', f'{campo} es obligatorio.'
        return '', None
    if len(valor) > maximo:
        return valor, f'{campo} no puede superar {maximo} caracteres.'
    return valor, None


def decimal_positivo(valor, campo, permitir_cero=False):
    """Convierte a float rechazando texto no numerico y valores negativos."""
    valor = (valor or '').strip()
    if not valor:
        return None, f'{campo} es obligatorio.'
    try:
        numero = float(valor)
    except ValueError:
        return None, f'{campo} debe ser un numero valido.'
    if numero != numero or numero in (float('inf'), float('-inf')):
        return None, f'{campo} debe ser un numero valido.'
    if numero < 0 or (numero == 0 and not permitir_cero):
        limite = 'mayor o igual a 0' if permitir_cero else 'mayor que 0'
        return None, f'{campo} debe ser {limite}.'
    return numero, None


def entero_no_negativo(valor, campo):
    """Convierte a int rechazando texto no numerico y valores negativos."""
    valor = (valor or '').strip()
    if not valor:
        return None, f'{campo} es obligatorio.'
    try:
        numero = int(valor)
    except ValueError:
        return None, f'{campo} debe ser un numero entero.'
    if numero < 0:
        return None, f'{campo} no puede ser negativo.'
    return numero, None


def opcion(valor, campo, permitidos):
    """Comprueba que el valor pertenezca a un conjunto cerrado."""
    valor = (valor or '').strip()
    if valor not in permitidos:
        return None, f'{campo} no es valido.'
    return valor, None


def mostrar_errores(errores):
    """Envia todos los errores al usuario mediante mensajes flash."""
    from flask import flash
    for error in errores:
        flash(error, 'danger')
