from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import joinedload

from app import db
from app.models.cliente.pedido import Pedido
from app.admin_required import admin_required
from app.validacion import opcion, mostrar_errores

bp = Blueprint('pedido_admin', __name__, url_prefix='/admin/pedidos')

POR_PAGINA = 15

# Estados permitidos. La plantilla los recorre para pintar el menu, y la ruta
# los usa como lista blanca: sin esto un POST manual guarda cualquier cadena.
ESTADOS = ('pendiente', 'pagado', 'enviado', 'entregado', 'cancelado')


@bp.route('/')
@admin_required
def index():
    pagina = request.args.get('pagina', 1, type=int)
    estado = request.args.get('estado', '', type=str).strip()

    consulta = Pedido.query.options(joinedload(Pedido.user))
    if estado in ESTADOS:
        consulta = consulta.filter(Pedido.estado == estado)

    paginacion = consulta.order_by(Pedido.fecha.desc()).paginate(
        page=pagina, per_page=POR_PAGINA, error_out=False)

    return render_template('admin/pedidos/index.html',
                           paginacion=paginacion,
                           pedidos=paginacion.items,
                           estados=ESTADOS,
                           estado_actual=estado)


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
