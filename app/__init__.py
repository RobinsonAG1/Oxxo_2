from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.exceptions import HTTPException

from app.security import init_csrf

db = SQLAlchemy()
login_manager = LoginManager()


@event.listens_for(Engine, "connect")
def _activar_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignora las claves foraneas salvo que se activen por conexion."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        # Otros motores (PostgreSQL, MySQL) ya las aplican y no conocen el PRAGMA.
        pass
    finally:
        cursor.close()


def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    init_csrf(app)

    @login_manager.user_loader
    def load_user(idUser):
        from .models.login.users import User
        return db.session.get(User, int(idUser))

    # Import all models so they are registered with SQLAlchemy
    from .models.login.users import User
    from .models.admin.categoria import Categoria
    from .models.admin.producto import Producto
    from .models.cliente.carrito import Carrito, CarritoItem
    from .models.cliente.pedido import Pedido, DetallePedido

    # Register blueprints organizados por rol
    from app.routes.login.auth import bp as auth_bp
    from app.routes.admin.productos import bp as producto_bp
    from app.routes.admin.categorias import bp as categoria_bp
    from app.routes.admin.pedidos import bp as pedido_admin_bp
    from app.routes.admin.usuarios import bp as usuario_bp
    from app.routes.cliente.tienda import bp as tienda_bp
    from app.routes.cliente.carrito import bp as carrito_bp
    from app.routes.cliente.pedidos import bp as pedido_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(pedido_admin_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(tienda_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(pedido_bp)

    @app.after_request
    def add_no_cache_headers(response):
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        """404, 403, 400... se muestran como pagina, conservando su codigo."""
        return render_template('error.html', codigo=e.code, mensaje=e.description), e.code

    @app.errorhandler(Exception)
    def handle_error(e):
        """Fallos no previstos: se registran completos, pero no se exponen."""
        app.logger.exception(e)
        db.session.rollback()
        return render_template(
            'error.html',
            codigo=500,
            mensaje='Ocurrio un error inesperado. Intentalo de nuevo mas tarde.',
        ), 500

    return app
