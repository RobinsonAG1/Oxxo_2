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
        from .models.login.users import User
        return User.query.get(int(idUser))

    # Import all models so they are registered with SQLAlchemy
    from .models.login.users import User
    from .models.admin.categoria import Categoria
    from .models.admin.producto import Producto
    from .models.cliente.carrito import Carrito, CarritoItem
    from .models.cliente.pedido import Pedido, DetallePedido

    # Register blueprints
    from app.routes import (
        auth, producto, categoria, carrito, pedido
    )
    app.register_blueprint(auth.bp)
    app.register_blueprint(producto.bp)
    app.register_blueprint(categoria.bp)
    app.register_blueprint(carrito.bp)
    app.register_blueprint(pedido.bp)

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