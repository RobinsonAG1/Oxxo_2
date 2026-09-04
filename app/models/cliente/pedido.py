from app import db
from datetime import datetime, timezone


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    idPedido = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.idUser'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estado = db.Column(db.String(30), nullable=False, default='pendiente')

    user = db.relationship('User', backref=db.backref('pedidos', lazy=True))
    detalles = db.relationship('DetallePedido', back_populates='pedido', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pedido {self.idPedido}>'


class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedidos'
    idDetalle = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.idPedido'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.idProducto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    pedido = db.relationship('Pedido', back_populates='detalles')
    producto = db.relationship('Producto', backref=db.backref('detalles', lazy='dynamic'))

    def subtotal(self):
        return float(self.precio) * self.cantidad

    def __repr__(self):
        return f'<DetallePedido {self.producto_id} x{self.cantidad}>'