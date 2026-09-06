from app import db


class Carrito(db.Model):
    __tablename__ = 'carritos'
    idCarrito = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.idUser'), nullable=False, unique=True)

    user = db.relationship('User', backref=db.backref('carrito', uselist=False))
    items = db.relationship('CarritoItem', back_populates='carrito', cascade='all, delete-orphan')

    def total(self):
        return sum(item.subtotal() for item in self.items)

    def __repr__(self):
        return f'<Carrito {self.user_id}>'


class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'
    idItem = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carritos.idCarrito'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.idProducto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)

    carrito = db.relationship('Carrito', back_populates='items')
    producto = db.relationship('Producto', backref=db.backref('carrito_items', lazy='dynamic'))

    def subtotal(self):
        return float(self.producto.precio) * self.cantidad

    def __repr__(self):
        return f'<CarritoItem {self.producto_id} x{self.cantidad}>'