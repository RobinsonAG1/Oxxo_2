from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.cliente.pedido import Pedido
from app.admin_required import admin_required

bp = Blueprint('pedido_admin', __name__, url_prefix='/pedido')


@bp.route('/')
@login_required
@admin_required
def index():
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('admin/pedidos/index.html', pedidos=pedidos)


@bp.route('/cambiar-estado/<int:id>', methods=['POST'])
@login_required
@admin_required
def cambiar_estado(id):
    pedido = Pedido.query.get_or_404(id)
    pedido.estado = request.form.get('estado', 'pendiente')
    db.session.commit()
    flash('Estado del pedido actualizado.', 'success')
    return redirect(url_for('pedido_admin.index'))