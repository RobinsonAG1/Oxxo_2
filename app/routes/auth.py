from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import User

bp = Blueprint('auth', __name__)


@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']

        user = User.query.filter_by(nameUser=nameUser).first()
        if user and user.check_password(passwordUser):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('auth.dashboard'))

        flash('Invalid credentials. Please try again.', 'danger')

    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return render_template("login.html")


@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == 'admin':
        from app.models.producto import Producto
        from app.models.pedido import Pedido
        from app.models.users import User
        from datetime import datetime, timedelta
        
        producto_count = Producto.query.count()
        pedido_count = Pedido.query.count()
        cliente_count = User.query.filter_by(rol='cliente').count()
        
        # Nuevas métricas
        productos_stock_bajo = Producto.query.filter(Producto.stock <= 10).all()
        productos_agotados = Producto.query.filter(Producto.stock == 0).count()
        pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()
        
        # Ventas del mes
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pedidos_mes = Pedido.query.filter(
            Pedido.fecha >= inicio_mes,
            Pedido.estado != 'cancelado'
        ).all()
        ventas_mes = sum(p.total for p in pedidos_mes)
        
        return render_template('dashboard.html',
                               producto_count=producto_count,
                               pedido_count=pedido_count,
                               cliente_count=cliente_count,
                               productos_stock_bajo=productos_stock_bajo,
                               productos_agotados=productos_agotados,
                               pedidos_pendientes=pedidos_pendientes,
                               ventas_mes=ventas_mes)
    return render_template('dashboard.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Limpiar completamente la sesion
    flash('You have been logged out.', 'info')
    response = make_response(redirect(url_for('auth.login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@bp.route('/check_auth')
@login_required
def check_auth():
    return {'authenticated': True}