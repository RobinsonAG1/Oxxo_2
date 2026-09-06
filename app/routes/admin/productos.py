from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import joinedload

from app import db
from app.models.admin.producto import Producto
from app.models.admin.categoria import Categoria
from app.admin_required import admin_required
from app.validacion import texto, decimal_positivo, entero_no_negativo, mostrar_errores

bp = Blueprint('producto', __name__, url_prefix='/Producto')

POR_PAGINA = 10


def _validar_formulario():
    """Valida el formulario de producto. Devuelve (datos, errores)."""
    errores = []

    nombre, error = texto(request.form.get('nombre'), 'El nombre', 150)
    if error:
        errores.append(error)

    descripcion, error = texto(request.form.get('descripcion'), 'La descripcion',
                               1000, obligatorio=False)
    if error:
        errores.append(error)

    precio, error = decimal_positivo(request.form.get('precio'), 'El precio')
    if error:
        errores.append(error)

    stock, error = entero_no_negativo(request.form.get('stock'), 'El stock')
    if error:
        errores.append(error)

    categoria_id, error = entero_no_negativo(request.form.get('categoria_id'), 'La categoria')
    if error:
        errores.append('Debes seleccionar una categoria.')
    elif db.session.get(Categoria, categoria_id) is None:
        errores.append('La categoria seleccionada no existe.')

    datos = {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio,
        'stock': stock,
        'categoria_id': categoria_id,
    }
    return datos, errores


@bp.route('/')
@admin_required
def index():
    busqueda = request.args.get('q', '', type=str).strip()
    pagina = request.args.get('pagina', 1, type=int)

    consulta = Producto.query.options(joinedload(Producto.categoria))
    if busqueda:
        consulta = consulta.filter(Producto.nombre.ilike(f'%{busqueda}%'))

    paginacion = consulta.order_by(Producto.nombre.asc()).paginate(
        page=pagina, per_page=POR_PAGINA, error_out=False)

    return render_template('admin/productos/index.html',
                           paginacion=paginacion,
                           productos=paginacion.items,
                           busqueda=busqueda)


@bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()

    if request.method == 'POST':
        datos, errores = _validar_formulario()
        if errores:
            mostrar_errores(errores)
            return render_template('admin/productos/add.html',
                                   categorias=categorias, valores=request.form)

        db.session.add(Producto(**datos))
        db.session.commit()
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('producto.index'))

    return render_template('admin/productos/add.html',
                           categorias=categorias, valores={})


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    producto = db.get_or_404(Producto, id)
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()

    if request.method == 'POST':
        # Se valida antes de tocar la entidad: si hay errores no debe quedar
        # ningun cambio a medias en la sesion de SQLAlchemy.
        datos, errores = _validar_formulario()
        if errores:
            mostrar_errores(errores)
            return render_template('admin/productos/edit.html', producto=producto,
                                   categorias=categorias, valores=request.form)

        for campo, valor in datos.items():
            setattr(producto, campo, valor)
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('producto.index'))

    valores = {
        'nombre': producto.nombre,
        'descripcion': producto.descripcion or '',
        'precio': producto.precio,
        'stock': producto.stock,
        'categoria_id': producto.categoria_id,
    }
    return render_template('admin/productos/edit.html', producto=producto,
                           categorias=categorias, valores=valores)


@bp.route('/detail/<int:id>')
@admin_required
def detail(id):
    producto = db.get_or_404(Producto, id)
    return render_template('admin/productos/detail.html', producto=producto)


@bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    producto = db.get_or_404(Producto, id)

    # Las filas de detalle_pedidos y carrito_items apuntan al producto. Borrarlo
    # dejaria pedidos historicos sin producto y romperia su consulta.
    if producto.detalles.first() is not None:
        flash(f'No se puede eliminar "{producto.nombre}": aparece en pedidos ya '
              f'realizados. Puedes dejarlo sin stock para retirarlo de la tienda.', 'danger')
        return redirect(url_for('producto.index'))

    if producto.carrito_items.first() is not None:
        flash(f'No se puede eliminar "{producto.nombre}": esta en el carrito de '
              f'algun cliente.', 'danger')
        return redirect(url_for('producto.index'))

    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('producto.index'))
