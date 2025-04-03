from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import dotenv
from datetime import datetime


# Configuração do Banco de Dados (Essas configs vem do arquivo .env)
dotenv.load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
secret_key = os.environ['SECRET_KEY']

# Instanciando a aplicação e o SQLAlchemy
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{user}:{password}@{host}/{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
print("Banco de dados Conectado!")

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = secret_key
app.secret_key = secret_key  # Necessário para sessões do login

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Classes / Models para as TABELAS

# 📌 Catequistas


class Catequistas(db.Model):
    __tablename__ = 'catequistas'

    id_catequista = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200))
    grupo = db.Column(db.String(100), default='Nao Especificado')
    nivel = db.Column(db.Enum('coordenador', 'catequista'),
                      nullable=False, default='catequista')

    # Relacionamentos
    crismandos = db.relationship(
        'Crismandos', backref='catequista', lazy=True, cascade="all, delete-orphan")
    usuario = db.relationship(
        'Usuarios', uselist=False, backref='catequista', cascade="all, delete-orphan")


# 📌 Crismandos
class Crismandos(db.Model):
    __tablename__ = 'crismandos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    # Foreign Key
    fk_id_catequista = db.Column(db.Integer, db.ForeignKey(
        'catequistas.id_catequista', ondelete='CASCADE', onupdate='CASCADE'))

    # Relacionamento com Frequencias
    frequencias = db.relationship(
        'Frequencias', backref='crismando', cascade="all, delete-orphan")


# 📌 Informações sobre Chamadas
class InforFrequencias(db.Model):
    __tablename__ = 'infor_frequencias'

    id_infor_freq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo_encontro = db.Column(db.String(250), nullable=False)
    data_chamada = db.Column(db.Date, nullable=False)


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

    # Foreign Key
    fk_id_catequista = db.Column(db.Integer, db.ForeignKey(
        'catequistas.id_catequista', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def get_id(self):
        return str(self.id_usuario)  # Flask-Login precisa desse método


@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuarios.query.filter_by(email=email).first()
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos!', 'danger')

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        id_catequista = request.form['fk_id_catequista']

        if Usuarios.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'warning')
        elif Usuarios.query.filter_by(fk_id_catequista=id_catequista).first():
            flash('Este catequista já possui um usuário!', 'warning')
        else:
            novo_usuario = Usuarios(
                email=email, fk_id_catequista=id_catequista)

            novo_usuario.set_password(senha)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))

    catequistas = Catequistas.query.with_entities(
        Catequistas.id_catequista, Catequistas.nome).all()
    return render_template('register.html', catequistas=catequistas)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


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


# Rota para exibir o formulário de frequência
@app.route("/fazer_frequencia", methods=["GET"])
def fazer_frequencia():
    # crismando = db.session.query(Crismandos).filter_by(id=id_crismando).first()
    lista_crismandos = Crismandos.query.filter_by(
        status_crismando='ativo').all()

    return render_template('fazer_frequencia.html', lista_crismandos=lista_crismandos)


# Rota para salvar a frequência no banco
@app.route("/salvar_frequencia", methods=["GET", "POST"])
def salvar_frequencia():
    if request.method == 'POST':
        titulo = request.form.get('titulo_encontro')
        data_chamada = request.form.get('data_chamada')

        # Criar registro em InforFrequencias
        nova_info_freq = InforFrequencias(titulo_encontro=titulo,
                                          data_chamada=datetime.strptime(data_chamada, '%Y-%m-%d'))
        db.session.add(nova_info_freq)
        db.session.commit()

        id_infor_freq = nova_info_freq.id_infor_freq

        # Salvar a frequência dos crismandos
        lista_crismandos = Crismandos.query.filter_by(
            status_crismando='ativo').all()

        for crismando in lista_crismandos:
            status = 'presente'
            if request.form.get(f'faltou_{crismando.id}'):
                status = 'falta'
            elif request.form.get(f'observacao_{crismando.id}'):
                status = 'justificada'

            observacao = request.form.get(f'observacao_{crismando.id}', None)
            nova_frequencia = Frequencias(
                status_frequencia=status,
                observacao=observacao,
                fk_id_crismando=crismando.id,
                fk_id_infor_freq=id_infor_freq
            )
            db.session.add(nova_frequencia)

        db.session.commit()
        flash("Frequencias registradas com sucesso!", "success")

        return redirect(url_for('listar_frequencias'))


# Rota para listar frequências registradas
@app.route('/listar_frequencias')
def listar_frequencias():
    data_filtro = request.args.get('data_filtro')  # Obtém a data do formulário
    # Obtém o titulo do formulário
    titulo_filtro = request.args.get('busca_titulo')

    query = InforFrequencias.query.order_by(
        InforFrequencias.data_chamada.desc())

    if data_filtro:  # Verifica se o usuário digitou algo no campo de data
        try:
            data_formatada = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(
                InforFrequencias.data_chamada == data_formatada)
        except ValueError:
            flash("Formato de data inválido!", "danger")

    if titulo_filtro:  # Verifica se o usuário digitou algo no campo de título
        query = query.filter(
            InforFrequencias.titulo_encontro.ilike(f"%{titulo_filtro}%"))
        # .ilike(f"%{---}") -> Utilizado para onde for texto

    registros_de_frequencias = query.all()  # Executa a consulta filtrada

    return render_template('historico_frequencias.html',
                           registros=registros_de_frequencias,
                           data_filtro=data_filtro,
                           titulo_filtro=titulo_filtro)


@app.route('/listar_frequencias/<int:id>', methods=['GET'])
def detalhes_frequencia(id):
    frequencia = InforFrequencias.query.get(id)
    if not frequencia:
        return "Frequência não encontrada", 404

    # Buscar todas as frequências associadas a essa chamada específica
    registros = Frequencias.query.filter_by(fk_id_infor_freq=id).all()

    return render_template('detalhes_frequencia.html', frequencia=frequencia, registros=registros)


if __name__ == "__main__":
    app.run(debug=True)
