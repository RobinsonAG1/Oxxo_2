from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    idUser = db.Column(db.Integer, primary_key=True)
    nameUser = db.Column(db.String(80), unique=True, nullable=False)
    passwordUser = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='cliente')

    def get_id(self):
        return str(self.idUser)

    def to_dict(self):
        return {
            "idUser": self.idUser,
            "nameUser": self.nameUser,
            "email": self.email,
            "rol": self.rol
        }

    def is_admin(self):
        return self.rol == 'admin'

    def set_password(self, password):
        self.passwordUser = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordUser, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.nameUser}>'