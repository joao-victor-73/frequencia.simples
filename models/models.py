from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



# Classes / Models para as TABELAS

# 📌 Catequistas
class Catequistas(db.Model):
    __tablename__ = 'catequistas'

    id_catequista = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200))
    nivel = db.Column(db.Enum('coordenador', 'catequista'),
                      nullable=False, default='catequista')
    tel1 = db.Column(db.String(20))
    fk_id_grupo = db.Column(db.Integer, db.ForeignKey(
        'grupos.id_grupo'), nullable=True)

    # Relacionamentos
    crismandos = db.relationship(
        'Crismandos', backref='catequista', lazy=True, cascade="all, delete-orphan")
    usuario = db.relationship(
        'Usuarios', uselist=False, backref='catequista', cascade="all, delete-orphan")

    grupo = db.relationship('Grupos', back_populates='catequistas')


# 📌 Crismandos
class Crismandos(db.Model):
    __tablename__ = 'crismandos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_mae = db.Column(db.String(100), nullable=False)
    nome_pai = db.Column(db.String(100), nullable=False,default='Nao mencionado')
    nome_padrim = db.Column(db.String(100), default="Não Tem")
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100))
    estado_civil = db.Column(db.String(200))
    possui_filhos = db.Column(db.String(10))
    possui_deficiencia = db.Column(db.String(50))
    tel1 = db.Column(db.String(20), nullable=False)
    tel2 = db.Column(db.String(20))
    batismo = db.Column(db.Enum('sim', 'nao'), default='nao')
    eucaristia = db.Column(db.Enum('sim', 'nao'), default='nao')
    status_crismando = db.Column(db.Enum('ativo', 'desistente'), default='ativo')
    fk_id_grupo = db.Column(db.Integer, db.ForeignKey('grupos.id_grupo'), nullable=True)

    # Foreign Key
    fk_id_catequista = db.Column(db.Integer, db.ForeignKey(
        'catequistas.id_catequista', ondelete='CASCADE', onupdate='CASCADE'))

    # Relacionamento com Frequencias
    frequencias = db.relationship(
        'Frequencias', backref='crismando', cascade="all, delete-orphan", lazy='dynamic')

    # Relacionamento com a tabela Grupos
    grupo = db.relationship('Grupos', backref='crismandos')


# 📌 Informações sobre os Grupos
class Grupos(db.Model):
    __tablename__ = 'grupos'

    id_grupo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_grupo = db.Column(db.String(100), nullable=False, unique=True)
    horario = db.Column(db.String(20))
    local_grupo = db.Column(db.String(100))
    descricao = db.Column(db.Text)

    # Relacionamentos
    catequistas = db.relationship('Catequistas', back_populates='grupo')

# 📌 Informações sobre Chamadas


class InforFrequencias(db.Model):
    __tablename__ = 'infor_frequencias'

    id_infor_freq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo_encontro = db.Column(db.String(250), nullable=False)
    data_chamada = db.Column(db.Date, nullable=False)

    fk_id_catequista = db.Column(db.Integer, db.ForeignKey(
        'catequistas.id_catequista', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    catequista = db.relationship(
        'Catequistas', backref='infor_frequencias', foreign_keys=[fk_id_catequista])


# 📌 Frequências dos Crismandos
class Frequencias(db.Model):
    __tablename__ = 'frequencias'

    id_freq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_frequencia = db.Column(
        db.Enum('presente', 'falta', 'justificada'), default='presente')
    observacao = db.Column(db.Text)

    # Foreign Keys
    fk_id_crismando = db.Column(db.Integer, db.ForeignKey(
        'crismandos.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    fk_id_infor_freq = db.Column(db.Integer, db.ForeignKey(
        'infor_frequencias.id_infor_freq', ondelete='CASCADE', onupdate='CASCADE'))


# 📌 Usuários (Login)
class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    avatar_perfil = db.Column(db.String(50))

    # Foreign Key
    fk_id_catequista = db.Column(db.Integer, db.ForeignKey(
        'catequistas.id_catequista', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        # Dentro da função check_password_hash, ele verifica se a senha_hash e a senha normal
        # são iguais ao decodificar, e retorna um BOOL (True para dizer que são iguais e
        # False se forem diferentes).
        return check_password_hash(self.senha_hash, senha)

    def get_id(self):
        # Flask-Login precisa desse método, dizendo qual que é o ID desse modelo.
        return str(self.id_usuario)