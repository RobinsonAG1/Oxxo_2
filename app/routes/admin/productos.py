from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.admin.producto import Producto
from app.models.admin.categoria import Categoria
from app.admin_required import admin_required

bp = Blueprint('producto', __name__, url_prefix='/Producto')


@bp.route('/')
@login_required
@admin_required
def index():
    productos = Producto.query.order_by(Producto.nombre.asc()).all()
    return render_template('admin/productos/index.html', productos=productos)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        categoria_id = int(request.form['categoria_id'])

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria_id=categoria_id
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('producto.index'))

    return render_template('admin/productos/add.html', categorias=categorias)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form.get('descripcion', '')
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        producto.categoria_id = int(request.form['categoria_id'])
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('producto.index'))

    return render_template('admin/productos/edit.html', producto=producto, categorias=categorias)


@bp.route('/detail/<int:id>')
@login_required
@admin_required
def detail(id):
    producto = Producto.query.get_or_404(id)
    return render_template('admin/productos/detail.html', producto=producto)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('producto.index'))