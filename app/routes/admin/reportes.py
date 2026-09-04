"""Reportes del panel de administracion.

Portado desde la rama Cliente, donde el modulo nunca llego a ejecutarse:
importaba rutas de la estructura antigua y no estaba registrado como blueprint.
"""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request
from sqlalchemy import desc, func

from app import db
from app.models.admin.producto import Producto
from app.models.cliente.pedido import Pedido, DetallePedido
from app.models.login.users import User
from app.admin_required import admin_required

bp = Blueprint('reportes', __name__, url_prefix='/admin/reportes')

UMBRAL_STOCK_BAJO = 10


def ahora():
    """Las fechas de los pedidos se guardan en UTC sin tzinfo.

    Comparar contra datetime.now() (hora local) desplazaba todos los periodos
    tantas horas como el huso del servidor, asi que se compara contra UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def rango_periodo(periodo):
    """Traduce el periodo pedido en la URL a un intervalo de fechas."""
    fin = ahora()
    if periodo == 'hoy':
        inicio = fin.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semana':
        inicio = fin - timedelta(days=7)
    elif periodo == 'anio':
        inicio = fin.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'mes':
        inicio = fin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        periodo = 'mes'
        inicio = fin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return periodo, inicio, fin


@bp.route('/')
@admin_required
def index():
    return render_template('admin/reportes/index.html')


@bp.route('/ventas')
@admin_required
def ventas():
    periodo, fecha_inicio, fecha_fin = rango_periodo(request.args.get('periodo', 'mes'))

    pedidos = Pedido.query.filter(
        Pedido.fecha >= fecha_inicio,
        Pedido.fecha <= fecha_fin,
        Pedido.estado != 'cancelado'
    ).order_by(Pedido.fecha.asc()).all()

    total_ventas = sum(float(p.total) for p in pedidos)
    total_pedidos = len(pedidos)
    ticket_promedio = total_ventas / total_pedidos if total_pedidos else 0

    ventas_por_dia = {}
    for pedido in pedidos:
        dia = pedido.fecha.strftime('%Y-%m-%d')
        ventas_por_dia[dia] = ventas_por_dia.get(dia, 0) + float(pedido.total)

    return render_template('admin/reportes/ventas.html',
                           total_ventas=total_ventas,
                           total_pedidos=total_pedidos,
                           ticket_promedio=ticket_promedio,
                           ventas_por_dia=ventas_por_dia,
                           periodo=periodo,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)


@bp.route('/productos-mas-vendidos')
@admin_required
def productos_mas_vendidos():
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
        Producto.idProducto, Producto.nombre, Producto.precio
    ).order_by(
        desc('total_vendido')
    ).limit(20).all()

    return render_template('admin/reportes/productos_mas_vendidos.html',
                           productos_vendidos=productos_vendidos)


@bp.route('/stock-bajo')
@admin_required
def stock_bajo():
    umbral = request.args.get('umbral', UMBRAL_STOCK_BAJO, type=int)
    if umbral is None or umbral < 0:
        umbral = UMBRAL_STOCK_BAJO

    productos_bajo_stock = (Producto.query
                            .filter(Producto.stock <= umbral)
                            .order_by(Producto.stock.asc())
                            .all())

    return render_template('admin/reportes/stock_bajo.html',
                           productos_bajo_stock=productos_bajo_stock,
                           umbral=umbral)


@bp.route('/resumen')
@admin_required
def resumen():
    inicio_mes = ahora().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    pedidos_mes = Pedido.query.filter(
        Pedido.fecha >= inicio_mes,
        Pedido.estado != 'cancelado'
    ).all()

    return render_template('admin/reportes/resumen.html',
                           ventas_mes=sum(float(p.total) for p in pedidos_mes),
                           pedidos_count=len(pedidos_mes),
                           productos_stock_bajo=Producto.query.filter(
                               Producto.stock <= UMBRAL_STOCK_BAJO).count(),
                           pedidos_pendientes=Pedido.query.filter_by(
                               estado='pendiente').count(),
                           total_productos=Producto.query.count(),
                           total_clientes=User.query.filter_by(rol='cliente').count())
