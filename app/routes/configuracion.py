from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.admin_required import admin_required

bp = Blueprint('configuracion', __name__, url_prefix='/admin/configuracion')


@bp.route('/')
@login_required
@admin_required
def index():
    return render_template('configuracion/index.html')


@bp.route('/tienda', methods=['GET', 'POST'])
@login_required
@admin_required
def tienda():
    # Aquí se podría implementar la configuración de la tienda
    # Por ahora es un placeholder
    if request.method == 'POST':
        nombre_tienda = request.form.get('nombre_tienda', 'OXXO')
        email_contacto = request.form.get('email_contacto', '')
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        
        # En una implementación real, esto se guardaría en una tabla de configuración
        flash('Configuración de tienda actualizada.', 'success')
        return redirect(url_for('configuracion.tienda'))
    
    return render_template('configuracion/tienda.html',
                          nombre_tienda='OXXO',
                          email_contacto='contacto@oxxo.com',
                          telefono='',
                          direccion='')


@bp.route('/stock', methods=['GET', 'POST'])
@login_required
@admin_required
def stock():
    if request.method == 'POST':
        umbral_bajo = request.form.get('umbral_bajo', 10, type=int)
        umbral_critico = request.form.get('umbral_critico', 5, type=int)
        
        # En una implementación real, esto se guardaría en configuración
        flash('Umbrales de stock actualizados.', 'success')
        return redirect(url_for('configuracion.stock'))
    
    return render_template('configuracion/stock.html',
                          umbral_bajo=10,
                          umbral_critico=5)
