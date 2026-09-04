from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.admin.categoria import Categoria
from app.admin_required import admin_required

bp = Blueprint('categoria', __name__, url_prefix='/Categoria')


@bp.route('/')
@login_required
@admin_required
def index():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    return render_template('admin/categorias/index.html', categorias=categorias)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        nueva = Categoria(nombre=nombre, descripcion=descripcion)
        db.session.add(nueva)
        db.session.commit()
        flash('Categoría creada exitosamente.', 'success')
        return redirect(url_for('categoria.index'))

    return render_template('admin/categorias/add.html')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        categoria.nombre = request.form['nombre']
        categoria.descripcion = request.form.get('descripcion', '')
        db.session.commit()
        flash('Categoría actualizada exitosamente.', 'success')
        return redirect(url_for('categoria.index'))

    return render_template('admin/categorias/edit.html', categoria=categoria)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.productos:
        flash('No se puede eliminar: la categoría tiene productos asociados.', 'danger')
        return redirect(url_for('categoria.index'))
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada exitosamente.', 'success')
    return redirect(url_for('categoria.index'))