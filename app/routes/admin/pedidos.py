from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import joinedload

from app import db
from app.models.cliente.pedido import Pedido
from app.models.login.users import User
from app.admin_required import admin_required
from app.validacion import opcion, mostrar_errores

bp = Blueprint('pedido_admin', __name__, url_prefix='/admin/pedidos')

POR_PAGINA = 15

# Estados permitidos. La plantilla los recorre para pintar el menu, y la ruta
# los usa como lista blanca: sin esto un POST manual guarda cualquier cadena.
ESTADOS = ('pendiente', 'pagado', 'enviado', 'entregado', 'cancelado')


def _fecha(valor):
    """Convierte el 'YYYY-MM-DD' de un <input type=date>; None si no es valido."""
    valor = (valor or '').strip()
    if not valor:
        return None
    try:
        return datetime.strptime(valor, '%Y-%m-%d')
    except ValueError:
        return None


@bp.route('/')
@admin_required
def index():
    pagina = request.args.get('pagina', 1, type=int)
    estado = request.args.get('estado', '', type=str).strip()
    cliente_id = request.args.get('cliente_id', type=int)
    fecha_inicio = request.args.get('fecha_inicio', '', type=str).strip()
    fecha_fin = request.args.get('fecha_fin', '', type=str).strip()

    consulta = Pedido.query.options(joinedload(Pedido.user))

    if estado in ESTADOS:
        consulta = consulta.filter(Pedido.estado == estado)
    if cliente_id:
        consulta = consulta.filter(Pedido.user_id == cliente_id)

    desde = _fecha(fecha_inicio)
    if desde:
        consulta = consulta.filter(Pedido.fecha >= desde)
    hasta = _fecha(fecha_fin)
    if hasta:
        # El input marca un dia; se incluye completo hasta las 23:59.
        consulta = consulta.filter(Pedido.fecha < hasta + timedelta(days=1))

    paginacion = consulta.order_by(Pedido.fecha.desc()).paginate(
        page=pagina, per_page=POR_PAGINA, error_out=False)

    return render_template('admin/pedidos/index.html',
                           paginacion=paginacion,
                           pedidos=paginacion.items,
                           estados=ESTADOS,
                           estado_actual=estado,
                           clientes=User.query.order_by(User.nameUser.asc()).all(),
                           cliente_id=cliente_id,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)


@bp.route('/cambiar-estado/<int:id>', methods=['POST'])
@admin_required
def cambiar_estado(id):
    pedido = db.get_or_404(Pedido, id)

    estado, error = opcion(request.form.get('estado'), 'El estado', set(ESTADOS))
    if error:
        mostrar_errores([error])
        return redirect(url_for('pedido_admin.index'))

    pedido.estado = estado
    db.session.commit()
    flash(f'Pedido #{pedido.idPedido} marcado como "{estado}".', 'success')
    return redirect(url_for('pedido_admin.index'))


@bp.route('/detalle/<int:id>')
@admin_required
def detalle(id):
    """Vista de detalle propia del panel, protegida por admin_required."""
    pedido = db.get_or_404(Pedido, id)
    return render_template('detalle_pedido.html', pedido=pedido, estados=ESTADOS)
