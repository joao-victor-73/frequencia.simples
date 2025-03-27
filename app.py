from flask import Flask, render_template, request
import os
import dotenv
from flask_sqlalchemy import SQLAlchemy


# Configuração do Banco de Dados (Essas configs vem do arquivo .env)
dotenv.load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']

# Instanciando a aplicação e o SQLAlchemy
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{user}:{password}@{host}/{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
print("Banco de dados Conectado!")

db = SQLAlchemy(app)


# Classes / Models para as TABELAS

class Catequistas(db.Model):
    __tablename__ = 'catequistas'

    id_catequista = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    grupo = db.Column(db.String(100), default='Nao Especificado')
    nivel = db.Column(db.Enum('coordenador', 'catequista'),
                      nullable=False, default='catequista')

    # (1:N - One-to-Many) UM catequista pode ter VÁRIOS crismandos
    crismandos = db.relationship('Crismandos', backref='cat', lazy=True)

    # (1:1 - One-to-One) UM login para apenas UM catequista
    login = db.relationship('Usuarios', uselist=False, backref='usuario')


class Crismandos(db.Model):
    __tablename__ = 'crismandos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_mae = db.Column(db.String(100), nullable=False)
    nome_pai = db.Column(db.String(100), nullable=False,
                         default='Nao mencionado')
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    tel1 = db.Column(db.String(15), nullable=False)
    tel2 = db.Column(db.String(15))
    batismo = db.Column(db.Enum('sim', 'nao'), default='nao')
    eucaristia = db.Column(db.Enum('sim', 'nao'), default='nao')
    status_crismando = db.Column(
        db.Enum('ativo', 'desistente'), default='ativo')

    # Chave Estrangeira (ForeignKey)
    fk_id_catequista = db.Column(
        db.Integer, db.ForeignKey('catequistas.id_catequista'))

    # (1:N) UM crismando pode ter VÁRIAS frequências
    frequencias = db.relationship('Frequencias', backref='cris')


class Frequencias(db.Model):
    __tablename__ = 'frequencias'

    id_freq = db.Column(db.Integer, primary_key=True)
    data_frequencia = db.Column(db.Date, nullable=False)
    status_frequencia = db.Column(
        db.Enum('presente', 'falta', 'justificada'), default='falta')
    observacao = db.Column(db.Text)

    # Chave Estrangeira
    fk_id_crismando = db.Column(db.Integer,
                                db.ForeignKey('crismandos.id'),
                                nullable=False)


class Usuarios(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

    # Chave Estrangeira
    fk_id_catequista = db.Column(db.Integer,
                                 db.ForeignKey('catequistas.id_catequista'),
                                 nullable=False)


# Rota de começo
@app.route("/", methods=["GET"])
def index():
    # lista_crismandos = Crismandos.query.all()
    # lista_crismandos = db.session.query(Crismandos, Catequistas).join(Catequistas).all()
    
    termo_procura = request.args.get('pesquisa', '').strip()

    query = db.session.query(Crismandos, Catequistas).join(Catequistas)

    if termo_procura:
        query = query.filter(Crismandos.nome.ilike(f"%{termo_procura}%"))

    lista_crismandos = query.all()

    return render_template('index.html', lista_crismandos=lista_crismandos, termo_procura=termo_procura)

    
    return render_template('index.html', lista_crismandos=lista_crismandos)


# Rota para registrar presença
@app.route("/registrar_presenca", methods=["POST"])
def registrar_presenca():
    pass

# Rota para consultar frequência


@app.route("/frequencia", methods=["GET"])
def listar_frequencia():
    pass


if __name__ == "__main__":
    app.run(debug=True)
