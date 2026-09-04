from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.users import User
from app.admin_required import admin_required

bp = Blueprint('usuario_admin', __name__, url_prefix='/admin/usuarios')


@bp.route('/')
@login_required
@admin_required
def index():
    usuarios = User.query.order_by(User.nameUser.asc()).all()
    return render_template('usuarios/index.html', usuarios=usuarios)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(nameUser=nameUser).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return render_template('usuarios/add.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('usuarios/add.html')
        
        nuevo = User(nameUser=nameUser, email=email, rol=rol)
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuario_admin.index'))
    
    return render_template('usuarios/add.html')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        usuario.nameUser = request.form['nameUser']
        usuario.email = request.form['email']
        usuario.rol = request.form['rol']
        
        # Si se proporciona nueva contraseña, actualizarla
        password = request.form.get('password')
        if password:
            usuario.set_password(password)
        
        db.session.commit()
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('usuario_admin.index'))
    
    return render_template('usuarios/edit.html', usuario=usuario)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    usuario = User.query.get_or_404(id)
    
    # No permitir eliminar el propio usuario
    if usuario.idUser == current_user.idUser:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('usuario_admin.index'))
    
    # Verificar si el usuario tiene pedidos
    if usuario.pedidos:
        flash('No se puede eliminar: el usuario tiene pedidos asociados.', 'danger')
        return redirect(url_for('usuario_admin.index'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('usuario_admin.index'))


@bp.route('/detail/<int:id>')
@login_required
@admin_required
def detail(id):
    from app.models.pedido import Pedido
    usuario = User.query.get_or_404(id)
    
    # Obtener historial de compras del cliente
    pedidos = Pedido.query.filter_by(user_id=id).order_by(Pedido.fecha.desc()).all()
    
    # Calcular total gastado
    total_gastado = sum(p.total for p in pedidos if p.estado != 'cancelado')
    
    return render_template('usuarios/detail.html', usuario=usuario, pedidos=pedidos, total_gastado=total_gastado)
