
from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps

def coordenador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.catequista.nivel != 'coordenador':
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for("crismando.index"))

        return f(*args, **kwargs)
    return decorated_function
