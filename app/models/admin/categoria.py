from app import db


class Categoria(db.Model):
    __tablename__ = 'categorias'
    idCategoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)

    productos = db.relationship('Producto', back_populates='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'