from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.cliente.pedido import Pedido, DetallePedido
from app.models.cliente.carrito import Carrito, CarritoItem
from app.models.admin.producto import Producto

bp = Blueprint('pedido', __name__, url_prefix='/pedido')


@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    carrito = Carrito.query.filter_by(user_id=current_user.idUser).first()
    if not carrito or not carrito.items:
        flash('Tu carrito está vacío.', 'danger')
        return redirect(url_for('carrito.ver_carrito'))

    total = 0
    pedido = Pedido(user_id=current_user.idUser)
    db.session.add(pedido)
    db.session.flush()

    for item in carrito.items:
        if item.cantidad > item.producto.stock:
            flash(f'No hay suficiente stock de "{item.producto.nombre}".', 'danger')
            db.session.rollback()
            return redirect(url_for('carrito.ver_carrito'))

        detalle = DetallePedido(
            pedido_id=pedido.idPedido,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio=item.producto.precio
        )
        db.session.add(detalle)
        item.producto.stock -= item.cantidad
        total += float(item.producto.precio) * item.cantidad

    pedido.total = total
    db.session.add(pedido)
    db.session.delete(carrito)
    db.session.commit()
    flash('Pedido realizado con éxito.', 'success')
    return redirect(url_for('pedido.mis_pedidos'))


@bp.route('/mis-pedidos')
@login_required
def mis_pedidos():
    pedidos = Pedido.query.filter_by(user_id=current_user.idUser).order_by(Pedido.fecha.desc()).all()
    return render_template('cliente/pedidos/mis_pedidos.html', pedidos=pedidos)


@bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    pedido = Pedido.query.get_or_404(id)
    if pedido.user_id != current_user.idUser and current_user.rol != 'admin':
        flash('No tienes permiso para ver este pedido.', 'danger')
        return redirect(url_for('auth.dashboard'))
    return render_template('detalle_pedido.html', pedido=pedido)