from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.admin.producto import Producto
from app.models.admin.categoria import Categoria

bp = Blueprint('tienda', __name__, url_prefix='/tienda')


@bp.route('/')
@login_required
def index():
    """Catálogo de la tienda visible para clientes."""
    categoria_id = request.args.get('categoria_id', type=int)
    if categoria_id:
        productos = Producto.query.filter_by(categoria_id=categoria_id).order_by(Producto.nombre.asc()).all()
    else:
        productos = Producto.query.order_by(Producto.nombre.asc()).all()
    categorias = Categoria.query.all()
    return render_template('cliente/tienda.html', productos=productos, categorias=categorias, categoria_id=categoria_id)