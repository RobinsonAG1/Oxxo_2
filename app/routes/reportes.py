from flask import Blueprint, render_template, request
from flask_login import login_required
from app import db
from app.models.pedido import Pedido, DetallePedido
from app.models.producto import Producto
from app.admin_required import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('reportes', __name__, url_prefix='/reportes')


@bp.route('/')
@login_required
@admin_required
def index():
    return render_template('reportes/index.html')


@bp.route('/ventas')
@login_required
@admin_required
def ventas():
    periodo = request.args.get('periodo', 'mes')
    
    hoy = datetime.now()
    
    if periodo == 'hoy':
        fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = hoy
    elif periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=7)
        fecha_fin = hoy
    elif periodo == 'mes':
        fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = hoy
    elif periodo == 'anio':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = hoy
    else:
        fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy
    
    pedidos = Pedido.query.filter(
        Pedido.fecha >= fecha_inicio,
        Pedido.fecha <= fecha_fin,
        Pedido.estado != 'cancelado'
    ).all()
    
    total_ventas = sum(p.total for p in pedidos)
    total_pedidos = len(pedidos)
    ticket_promedio = total_ventas / total_pedidos if total_pedidos > 0 else 0
    
    # Ventas por día
    ventas_por_dia = {}
    for pedido in pedidos:
        fecha = pedido.fecha.strftime('%Y-%m-%d')
        if fecha not in ventas_por_dia:
            ventas_por_dia[fecha] = 0
        ventas_por_dia[fecha] += float(pedido.total)
    
    return render_template('reportes/ventas.html', 
                          total_ventas=total_ventas,
                          total_pedidos=total_pedidos,
                          ticket_promedio=ticket_promedio,
                          ventas_por_dia=ventas_por_dia,
                          periodo=periodo,
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)


@bp.route('/productos-mas-vendidos')
@login_required
@admin_required
def productos_mas_vendidos():
    from sqlalchemy import desc
    
    # Query para obtener productos más vendidos
    productos_vendidos = db.session.query(
        Producto.idProducto,
        Producto.nombre,
        Producto.precio,
        func.sum(DetallePedido.cantidad).label('total_vendido'),
        func.sum(DetallePedido.cantidad * DetallePedido.precio).label('total_ingresos')
    ).join(
        DetallePedido, Producto.idProducto == DetallePedido.producto_id
    ).join(
        Pedido, DetallePedido.pedido_id == Pedido.idPedido
    ).filter(
        Pedido.estado != 'cancelado'
    ).group_by(
        Producto.idProducto,
        Producto.nombre,
        Producto.precio
    ).order_by(
        desc('total_vendido')
    ).limit(20).all()
    
    return render_template('reportes/productos_mas_vendidos.html', 
                          productos_vendidos=productos_vendidos)


@bp.route('/stock-bajo')
@login_required
@admin_required
def stock_bajo():
    umbral = request.args.get('umbral', 10, type=int)
    
    productos_bajo_stock = Producto.query.filter(
        Producto.stock <= umbral
    ).order_by(Producto.stock.asc()).all()
    
    return render_template('reportes/stock_bajo.html',
                          productos_bajo_stock=productos_bajo_stock,
                          umbral=umbral)


@bp.route('/resumen')
@login_required
@admin_required
def resumen():
    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Métricas del mes
    pedidos_mes = Pedido.query.filter(
        Pedido.fecha >= inicio_mes,
        Pedido.estado != 'cancelado'
    ).all()
    
    ventas_mes = sum(p.total for p in pedidos_mes)
    pedidos_count = len(pedidos_mes)
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.query.filter(Producto.stock <= 10).count()
    
    # Pedidos pendientes
    pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').count()
    
    # Total productos
    total_productos = Producto.query.count()
    
    # Total clientes
    from app.models.users import User
    total_clientes = User.query.filter_by(rol='cliente').count()
    
    return render_template('reportes/resumen.html',
                          ventas_mes=ventas_mes,
                          pedidos_count=pedidos_count,
                          productos_stock_bajo=productos_stock_bajo,
                          pedidos_pendientes=pedidos_pendientes,
                          total_productos=total_productos,
                          total_clientes=total_clientes)
