from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Decorador que restringe el acceso a usuarios con rol administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.rol != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def cliente_required(f):
    """Decorador que restringe el acceso a usuarios con rol cliente."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.rol != 'cliente':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function