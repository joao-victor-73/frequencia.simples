from flask import Flask, render_template, request, redirect, url_for
import os
import dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



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
    crismandos = db.relationship('Crismandos', backref='catequista', lazy=True)

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
    cidade = db.Column(db.String(100))
    tel1 = db.Column(db.String(20), nullable=False)
    tel2 = db.Column(db.String(20))
    batismo = db.Column(db.Enum('sim', 'nao'), default='nao')
    eucaristia = db.Column(db.Enum('sim', 'nao'), default='nao')
    status_crismando = db.Column(
        db.Enum('ativo', 'desistente'), default='ativo')

    # Chave Estrangeira (ForeignKey)
    fk_id_catequista = db.Column(
        db.Integer, db.ForeignKey('catequistas.id_catequista'))

    # (1:N) UM crismando pode ter VÁRIAS frequências
    frequencias = db.relationship('Frequencias', backref='crismando')


class Frequencias(db.Model):
    __tablename__ = 'frequencias'

    id_freq = db.Column(db.Integer, primary_key=True)
    data_frequencia = db.Column(db.Date, nullable=False)
    status_frequencia = db.Column(
        db.Enum('presente', 'falta', 'justificada'), default='presente')
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

    # Obter os valores de busca da URL que vem da pagina index.html
    search_term = request.args.get('busca', '').strip()
    status_filter = request.args.get(
        'buscar_status_crismando', '').strip()  # obtém o status selecionado

    # Pega o valor se o checkbox foi marcado
    filtrar_batizado = request.args.get('batismo')

    # Pega o valor se o checkbox foi marcado
    filtrar_eucaristia = request.args.get('eucaristia')

    # Join entre as tabelas Crismandos e Catequistas
    query = db.session.query(Crismandos, Catequistas).join(Catequistas)

    # Se o usuário digitou um nome, aplicamos um filtro de nome:
    if search_term:
        query = query.filter(Crismandos.nome.ilike(f"%{search_term}%"))

    # Se o usuário escolheu um filtro, aplicamos o filtro de status:
    if status_filter:
        query = query.filter(Crismandos.status_crismando == status_filter)

    # Filtro por batismo (1 = Sim | 0 - Não)
    if filtrar_batizado is not None:
        query = query.filter(Crismandos.batismo == (
            'sim' if filtrar_batizado == '1' else 'nao'))

    # Filtro por eucaristia (1 = Sim | 0 - Não)
    if filtrar_eucaristia is not None:
        query = query.filter(Crismandos.eucaristia == (
            'sim' if filtrar_eucaristia == '1' else 'nao'))

    # Ordenação alfabética dos resultados
    query = query.order_by(Crismandos.nome)

    # Executamos a consulta e pegamos os resultados
    lista_crismandos = query.all()

    return render_template('index.html',
                           lista_crismandos=lista_crismandos,
                           search_term=search_term,
                           # Garantindo a persistência dos filtros de Batismo e Eucaristia
                           status_crismando=request.args.get(
                               'buscar_status_crismando', ''),
                           status_filter=status_filter,
                           filtrar_batizado=filtrar_batizado,
                           filtrar_eucaristia=filtrar_eucaristia)


# Rota para editar informações dos crismandos
@app.route("/editar_informacoes/<int:id_crismando>", methods=['POST', 'GET'])
def editar_infor(id_crismando):

    # Obtendo os dados associados ao id do crismando
    crismando = db.session.query(Crismandos).filter_by(id=id_crismando).first()
    lista_catequistas = db.session.query(Catequistas)

    if not crismando:
        return "Crismando não encontrado", 404

    return render_template('infor_crismandos.html', crismando=crismando, lista_catequistas=lista_catequistas)


# Rota para salvar alterações nas informações dos crismandos
@app.route("/atualizar_informacoes", methods=['POST', ])
def atualizar_infor():

    # Pega o id do crismando. (esse id vem de um input hidden la no template 'infor_crismandos')
    atualiza_crismando = Crismandos.query.filter_by(
        id=request.form['id_crismando']).first()

    atualiza_crismando.nome = request.form['nome_crismando']
    atualiza_crismando.data_nascimento = request.form['data_nascimento']
    atualiza_crismando.tel1 = request.form['telefone1']
    atualiza_crismando.tel2 = request.form['telefone2']
    atualiza_crismando.nome_mae = request.form['nome_mae']
    atualiza_crismando.nome_pai = request.form['nome_pai']
    atualiza_crismando.endereco = request.form['endereco']
    atualiza_crismando.cidade = request.form['cidade']
    atualiza_crismando.status_crismando = request.form['status_crismando']
    atualiza_crismando.batismo = request.form['batismo']
    atualiza_crismando.eucaristia = request.form['eucaristia']

    # Atualiza o catequista responsável (pega o id da mesma maneira que o do crismando)
    # Atualiza a FK do catequista
    atualiza_crismando.fk_id_catequista = request.form['catequista_responsavel']

    try:
        db.session.add(atualiza_crismando)
        db.session.commit()
    except Exception as e:
        print("Erro ao salvar no banco de dados: ", str(e))
        db.session.rollback()

    return redirect(url_for('index'))


# Rota para registrar presença
@app.route("/registrar_freq", methods=["POST", "GET"])
def registrar_frequencia():
    if request.method == 'POST':
        data_frequencia = request.form['data_frequencia']

        for crismando_id, status in request.form.items():

            if crismando_id != 'data_frequencia':
                crismando = Crismandos.query.get(crismando_id)

                if crismando:
                    nova_frequencia = Frequencias(
                        fk_id_crismando=crismando.id,
                        data_frequencia=data_frequencia,
                        status_frequencia=status
                    )
                    db.session.add(nova_frequencia)

        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('frequencia.html', crismandos=Crismandos.query.all())


# Rota para consultar frequência
@app.route("/frequencia", methods=["GET"])
def listar_frequencia():
    # crismando = db.session.query(Crismandos).filter_by(id=id_crismando).first()
    lista_crismandos = db.session.query(Crismandos)

    return render_template('frequencia.html', lista_crismandos=lista_crismandos)


@app.route("/ver_frequencias")
def ver_frequencias():
    frequencias = Frequencias.query.all()
    return render_template('visualizar_frequencias.html', frequencias=frequencias)



if __name__ == "__main__":
    app.run(debug=True)
