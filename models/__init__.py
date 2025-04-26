from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .models import Catequistas, Crismandos, Grupos, Frequencias, InforFrequencias, Usuarios
