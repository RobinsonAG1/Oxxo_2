from app import db


class Producto(db.Model):
    __tablename__ = 'productos'
    idProducto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.idCategoria'), nullable=False)

    categoria = db.relationship('Categoria', back_populates='productos')

    def to_dict(self):
        return {
            "idProducto": self.idProducto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": float(self.precio) if self.precio else 0,
            "stock": self.stock,
            "categoria": self.categoria.nombre if self.categoria else None
        }

    def __repr__(self):
        return f'<Producto {self.nombre}>'