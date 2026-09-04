from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(idUser):
        from .models.users import User
        return User.query.get(int(idUser))

    # Import all models so they are registered with SQLAlchemy
    from .models.users import User
    from .models.categoria import Categoria
    from .models.producto import Producto
    from .models.carrito import Carrito, CarritoItem
    from .models.pedido import Pedido, DetallePedido

    # Register blueprints organizados por rol
    from app.routes.auth import bp as auth_bp
    from app.routes.producto import bp as producto_bp
    from app.routes.categoria import bp as categoria_bp
    from app.routes.pedido import bp as pedido_bp
    from app.routes.usuarios import bp as usuarios_bp
    from app.routes.carrito import bp as carrito_bp
    from app.routes.reportes import bp as reportes_bp
    from app.routes.configuracion import bp as configuracion_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(configuracion_bp)

    @app.after_request
    def add_no_cache_headers(response):
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    @app.errorhandler(Exception)
    def handle_error(e):
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}, 500

    return app