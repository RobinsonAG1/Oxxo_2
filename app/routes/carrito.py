from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.producto import Producto
from app.models.carrito import Carrito, CarritoItem

bp = Blueprint('carrito', __name__, url_prefix='/carrito')


def obtener_carrito(user_id):
    """Obtiene o crea el carrito del usuario actual."""
    carrito = Carrito.query.filter_by(user_id=user_id).first()
    if not carrito:
        carrito = Carrito(user_id=user_id)
        db.session.add(carrito)
        db.session.commit()
    return carrito


@bp.route('/')
@login_required
def ver_carrito():
    carrito = obtener_carrito(current_user.idUser)
    return render_template('carrito/ver.html', carrito=carrito)


@bp.route('/add/<int:producto_id>', methods=['POST'])
@login_required
def agregar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    carrito = obtener_carrito(current_user.idUser)

    item = CarritoItem.query.filter_by(carrito_id=carrito.idCarrito, producto_id=producto.idProducto).first()
    if item:
        item.cantidad += 1
    else:
        item = CarritoItem(carrito_id=carrito.idCarrito, producto_id=producto.idProducto, cantidad=1)
        db.session.add(item)

    db.session.commit()
    flash(f'"{producto.nombre}" agregado al carrito.', 'success')
    return redirect(url_for('carrito.ver_carrito'))


@bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def actualizar(item_id):
    item = CarritoItem.query.get_or_404(item_id)
    if item.carrito.user_id != current_user.idUser:
        flash('No tienes permiso para modificar este carrito.', 'danger')
        return redirect(url_for('carrito.ver_carrito'))

    nueva_cantidad = int(request.form.get('cantidad', 1))
    if nueva_cantidad <= 0:
        db.session.delete(item)
    else:
        item.cantidad = nueva_cantidad
    db.session.commit()
    flash('Carrito actualizado.', 'success')
    return redirect(url_for('carrito.ver_carrito'))


@bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def eliminar(item_id):
    item = CarritoItem.query.get_or_404(item_id)
    if item.carrito.user_id != current_user.idUser:
        flash('No tienes permiso para modificar este carrito.', 'danger')
        return redirect(url_for('carrito.ver_carrito'))

    db.session.delete(item)
    db.session.commit()
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('carrito.ver_carrito'))