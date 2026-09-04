from app import create_app, db


def seed_data():
    """Crea un usuario administrador, categorias y productos de ejemplo."""
    from app.models.users import User
    from app.models.categoria import Categoria
    from app.models.producto import Producto

    if not User.query.filter_by(nameUser='admin').first():
        admin = User(nameUser='admin', email='admin@oxxo.com', rol='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if not User.query.filter_by(nameUser='cliente').first():
        cliente = User(nameUser='cliente', email='cliente@oxxo.com', rol='cliente')
        cliente.set_password('cliente123')
        db.session.add(cliente)

    categorias = [
        {'nombre': 'Botanas', 'descripcion': 'Papas, cacahuates y botanas'},
        {'nombre': 'Bebidas', 'descripcion': 'Refrescos, jugos y agua'},
        {'nombre': 'Dulces', 'descripcion': 'Dulces y chicles'},
        {'nombre': 'Panadería', 'descripcion': 'Pan y galletas'},
        {'nombre': 'Artículos de Limpieza', 'descripcion': 'Productos para el hogar'},
    ]

    categorias_creadas = {}
    for cat in categorias:
        if not Categoria.query.filter_by(nombre=cat['nombre']).first():
            nueva = Categoria(nombre=cat['nombre'], descripcion=cat['descripcion'])
            db.session.add(nueva)
            db.session.flush()
            categorias_creadas[cat['nombre']] = nueva

    db.session.flush()

    productos = [
        {'nombre': 'Papas Sabritas', 'precio': 28.0, 'stock': 50, 'categoria': 'Botanas', 'descripcion': 'Sabritas originales 60g'},
        {'nombre': 'Ruffles', 'precio': 30.0, 'stock': 40, 'categoria': 'Botanas', 'descripcion': 'Ruffles queso 60g'},
        {'nombre': 'Coca-Cola', 'precio': 25.0, 'stock': 80, 'categoria': 'Bebidas', 'descripcion': 'Coca-Cola 600ml'},
        {'nombre': 'Agua Bonafont', 'precio': 15.0, 'stock': 100, 'categoria': 'Bebidas', 'descripcion': 'Agua natural 1L'},
        {'nombre': 'Chocolate', 'precio': 20.0, 'stock': 60, 'categoria': 'Dulces', 'descripcion': 'Barra de chocolate 45g'},
        {'nombre': 'Gansito', 'precio': 22.0, 'stock': 45, 'categoria': 'Panadería', 'descripcion': 'Gansito marinela'},
        {'nombre': 'Galletas Emperador', 'precio': 24.0, 'stock': 55, 'categoria': 'Panadería', 'descripcion': 'Galletas de vainilla'},
    ]

    for prod in productos:
        if not Producto.query.filter_by(nombre=prod['nombre']).first():
            nuevo = Producto(
                nombre=prod['nombre'],
                precio=prod['precio'],
                stock=prod['stock'],
                descripcion=prod['descripcion'],
                categoria_id=categorias_creadas[prod['categoria']].idCategoria
            )
            db.session.add(nuevo)

    db.session.commit()
    print("Datos de ejemplo creados: admin/admin123, cliente/cliente123")


app = create_app()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)