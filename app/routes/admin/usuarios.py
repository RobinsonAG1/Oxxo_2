import re

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import func

from app import db
from app.models.login.users import User
from app.models.cliente.carrito import Carrito
from app.models.cliente.pedido import Pedido
from app.admin_required import admin_required
from app.validacion import texto, opcion, mostrar_errores

bp = Blueprint('usuario', __name__, url_prefix='/Usuario')

POR_PAGINA = 10
ROLES = ('admin', 'cliente')
LONGITUD_MINIMA_PASSWORD = 6

_FORMATO_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _total_admins(excluir_id=None):
    consulta = User.query.filter_by(rol='admin')
    if excluir_id is not None:
        consulta = consulta.filter(User.idUser != excluir_id)
    return consulta.count()


def _duplicado(columna, valor, excluir_id=None):
    """Comprueba unicidad sin distinguir mayusculas, como espera el usuario."""
    consulta = User.query.filter(func.lower(columna) == valor.lower())
    if excluir_id is not None:
        consulta = consulta.filter(User.idUser != excluir_id)
    return consulta.first() is not None


def _validar_formulario(excluir_id=None, password_obligatoria=True):
    """Valida el formulario de usuario. Devuelve (datos, errores)."""
    errores = []

    nombre, error = texto(request.form.get('nameUser'), 'El nombre de usuario', 80)
    if error:
        errores.append(error)
    elif _duplicado(User.nameUser, nombre, excluir_id):
        errores.append(f'Ya existe un usuario llamado "{nombre}".')

    email, error = texto(request.form.get('email'), 'El correo', 120)
    if error:
        errores.append(error)
    elif not _FORMATO_EMAIL.match(email):
        errores.append('El correo no tiene un formato valido.')
    elif _duplicado(User.email, email, excluir_id):
        errores.append(f'El correo "{email}" ya esta registrado.')

    rol, error = opcion(request.form.get('rol'), 'El rol', set(ROLES))
    if error:
        errores.append(error)

    password = request.form.get('passwordUser') or ''
    if password_obligatoria or password:
        if len(password) < LONGITUD_MINIMA_PASSWORD:
            errores.append(f'La contrasena debe tener al menos '
                           f'{LONGITUD_MINIMA_PASSWORD} caracteres.')
        elif password != request.form.get('passwordConfirm', ''):
            errores.append('Las contrasenas no coinciden.')

    datos = {'nameUser': nombre, 'email': email, 'rol': rol, 'password': password}
    return datos, errores


@bp.route('/')
@admin_required
def index():
    busqueda = request.args.get('q', '', type=str).strip()
    rol = request.args.get('rol', '', type=str).strip()
    pagina = request.args.get('pagina', 1, type=int)

    consulta = User.query
    if busqueda:
        patron = f'%{busqueda}%'
        consulta = consulta.filter(db.or_(User.nameUser.ilike(patron),
                                          User.email.ilike(patron)))
    if rol in ROLES:
        consulta = consulta.filter(User.rol == rol)

    paginacion = consulta.order_by(User.nameUser.asc()).paginate(
        page=pagina, per_page=POR_PAGINA, error_out=False)

    # Numero de pedidos por usuario, en una sola consulta agregada.
    conteos = dict(db.session.query(Pedido.user_id, func.count(Pedido.idPedido))
                   .group_by(Pedido.user_id).all())

    return render_template('admin/usuarios/index.html',
                           paginacion=paginacion,
                           usuarios=paginacion.items,
                           conteos=conteos,
                           roles=ROLES,
                           busqueda=busqueda,
                           rol_actual=rol)


@bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    if request.method == 'POST':
        datos, errores = _validar_formulario()
        if errores:
            mostrar_errores(errores)
            return render_template('admin/usuarios/add.html',
                                   roles=ROLES, valores=request.form)

        usuario = User(nameUser=datos['nameUser'], email=datos['email'], rol=datos['rol'])
        usuario.set_password(datos['password'])
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuario "{usuario.nameUser}" creado exitosamente.', 'success')
        return redirect(url_for('usuario.index'))

    return render_template('admin/usuarios/add.html', roles=ROLES, valores={})


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    usuario = db.get_or_404(User, id)

    if request.method == 'POST':
        datos, errores = _validar_formulario(excluir_id=usuario.idUser,
                                             password_obligatoria=False)

        # Sin esta comprobacion el panel puede quedarse sin ningun administrador.
        if (not errores and usuario.rol == 'admin' and datos['rol'] != 'admin'
                and _total_admins(excluir_id=usuario.idUser) == 0):
            errores.append('No puedes quitar el rol de administrador al ultimo '
                           'administrador que queda.')

        if errores:
            mostrar_errores(errores)
            return render_template('admin/usuarios/edit.html', usuario=usuario,
                                   roles=ROLES, valores=request.form)

        usuario.nameUser = datos['nameUser']
        usuario.email = datos['email']
        usuario.rol = datos['rol']
        if datos['password']:
            usuario.set_password(datos['password'])
        db.session.commit()
        flash(f'Usuario "{usuario.nameUser}" actualizado exitosamente.', 'success')
        return redirect(url_for('usuario.index'))

    valores = {'nameUser': usuario.nameUser, 'email': usuario.email, 'rol': usuario.rol}
    return render_template('admin/usuarios/edit.html', usuario=usuario,
                           roles=ROLES, valores=valores)


@bp.route('/detail/<int:id>')
@admin_required
def detail(id):
    """Ficha del usuario con su historial de compras."""
    usuario = db.get_or_404(User, id)
    pedidos = (Pedido.query.filter_by(user_id=usuario.idUser)
               .order_by(Pedido.fecha.desc()).all())
    # Los pedidos cancelados no cuentan para el gasto acumulado.
    total_gastado = sum(float(p.total) for p in pedidos if p.estado != 'cancelado')
    return render_template('admin/usuarios/detail.html', usuario=usuario,
                           pedidos=pedidos, total_gastado=total_gastado)


@bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    usuario = db.get_or_404(User, id)

    if usuario.idUser == current_user.idUser:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('usuario.index'))

    if usuario.rol == 'admin' and _total_admins(excluir_id=usuario.idUser) == 0:
        flash('No puedes eliminar al ultimo administrador.', 'danger')
        return redirect(url_for('usuario.index'))

    total_pedidos = Pedido.query.filter_by(user_id=usuario.idUser).count()
    if total_pedidos:
        flash(f'No se puede eliminar "{usuario.nameUser}": tiene {total_pedidos} '
              f'pedido(s) en el historial.', 'danger')
        return redirect(url_for('usuario.index'))

    # El carrito referencia al usuario: hay que retirarlo antes del borrado.
    carrito = Carrito.query.filter_by(user_id=usuario.idUser).first()
    if carrito:
        db.session.delete(carrito)

    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('usuario.index'))
