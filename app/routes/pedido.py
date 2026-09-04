from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.pedido import Pedido, DetallePedido
from app.models.carrito import Carrito, CarritoItem
from app.models.producto import Producto
from app.admin_required import admin_required

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
    return render_template('pedido/mis_pedidos.html', pedidos=pedidos)


@bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    pedido = Pedido.query.get_or_404(id)
    if pedido.user_id != current_user.idUser and current_user.rol != 'admin':
        flash('No tienes permiso para ver este pedido.', 'danger')
        return redirect(url_for('auth.dashboard'))
    return render_template('pedido/detalle.html', pedido=pedido)


@bp.route('/')
@login_required
@admin_required
def index():
    estado_filtro = request.args.get('estado', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    cliente_id = request.args.get('cliente_id', '', type=int)
    
    query = Pedido.query
    
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    
    if fecha_inicio:
        from datetime import datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        query = query.filter(Pedido.fecha >= fecha_inicio_dt)
    
    if fecha_fin:
        from datetime import datetime
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        query = query.filter(Pedido.fecha <= fecha_fin_dt)
    
    if cliente_id:
        query = query.filter_by(user_id=cliente_id)
    
    pedidos = query.order_by(Pedido.fecha.desc()).all()
    
    from app.models.users import User
    clientes = User.query.filter_by(rol='cliente').all()
    
    return render_template('pedido/index.html', pedidos=pedidos, clientes=clientes,
                          estado_filtro=estado_filtro, fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin, cliente_id=cliente_id)


@bp.route('/cambiar-estado/<int:id>', methods=['POST'])
@login_required
@admin_required
def cambiar_estado(id):
    pedido = Pedido.query.get_or_404(id)
    pedido.estado = request.form.get('estado', 'pendiente')
    db.session.commit()
    flash('Estado del pedido actualizado.', 'success')
    return redirect(url_for('pedido.index'))