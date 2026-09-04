from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func

from app import db
from app.models.admin.categoria import Categoria
from app.models.admin.producto import Producto
from app.admin_required import admin_required
from app.validacion import texto, mostrar_errores

bp = Blueprint('categoria', __name__, url_prefix='/Categoria')

POR_PAGINA = 10


def _validar_formulario(excluir_id=None):
    """Valida el formulario de categoria. Devuelve (datos, errores)."""
    errores = []

    nombre, error = texto(request.form.get('nombre'), 'El nombre', 100)
    if error:
        errores.append(error)
    elif _nombre_duplicado(nombre, excluir_id):
        errores.append(f'Ya existe una categoria llamada "{nombre}".')

    descripcion, error = texto(request.form.get('descripcion'), 'La descripcion',
                               255, obligatorio=False)
    if error:
        errores.append(error)

    return {'nombre': nombre, 'descripcion': descripcion}, errores


def _nombre_duplicado(nombre, excluir_id=None):
    """El nombre es unique en la base: se comprueba antes para evitar el error SQL."""
    consulta = Categoria.query.filter(func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.filter(Categoria.idCategoria != excluir_id)
    return consulta.first() is not None


def _conteo_productos():
    """Numero de productos por categoria en una sola consulta agregada."""
    filas = (db.session.query(Producto.categoria_id, func.count(Producto.idProducto))
             .group_by(Producto.categoria_id).all())
    return dict(filas)


@bp.route('/')
@admin_required
def index():
    pagina = request.args.get('pagina', 1, type=int)
    paginacion = Categoria.query.order_by(Categoria.nombre.asc()).paginate(
        page=pagina, per_page=POR_PAGINA, error_out=False)

    return render_template('admin/categorias/index.html',
                           paginacion=paginacion,
                           categorias=paginacion.items,
                           conteos=_conteo_productos())


@bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    if request.method == 'POST':
        datos, errores = _validar_formulario()
        if errores:
            mostrar_errores(errores)
            return render_template('admin/categorias/add.html', valores=request.form)

        db.session.add(Categoria(**datos))
        db.session.commit()
        flash('Categoria creada exitosamente.', 'success')
        return redirect(url_for('categoria.index'))

    return render_template('admin/categorias/add.html', valores={})


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    categoria = db.get_or_404(Categoria, id)

    if request.method == 'POST':
        datos, errores = _validar_formulario(excluir_id=categoria.idCategoria)
        if errores:
            mostrar_errores(errores)
            return render_template('admin/categorias/edit.html',
                                   categoria=categoria, valores=request.form)

        categoria.nombre = datos['nombre']
        categoria.descripcion = datos['descripcion']
        db.session.commit()
        flash('Categoria actualizada exitosamente.', 'success')
        return redirect(url_for('categoria.index'))

    valores = {'nombre': categoria.nombre, 'descripcion': categoria.descripcion or ''}
    return render_template('admin/categorias/edit.html',
                           categoria=categoria, valores=valores)


@bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    categoria = db.get_or_404(Categoria, id)

    total = Producto.query.filter_by(categoria_id=categoria.idCategoria).count()
    if total:
        flash(f'No se puede eliminar: la categoria tiene {total} producto(s) '
              f'asociado(s).', 'danger')
        return redirect(url_for('categoria.index'))

    db.session.delete(categoria)
    db.session.commit()
    flash('Categoria eliminada exitosamente.', 'success')
    return redirect(url_for('categoria.index'))
