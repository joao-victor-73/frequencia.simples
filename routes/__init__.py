
from .auth_routes import auth_bp
from .catequistas_routes import catequista_bp
from .crismandos_routes import crismando_bp
from .grupos_routes import grupos_bp
from .frequencias_routes import frequencias_bp
from .others_routes import others_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(catequista_bp)
    app.register_blueprint(crismando_bp)
    app.register_blueprint(grupos_bp)
    app.register_blueprint(frequencias_bp)
    app.register_blueprint(others_bp)
