from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.models import Usuarios, Catequistas, Crismandos, Grupos, Frequencias, InforFrequencias
from flask_login import login_required
from utils.decorators import coordenador_required
from models import db
import sqlalchemy as sa


# Criação do Blueprint
crismando_bp = Blueprint('crismando_bp', __name__)  # nome do blueprint


# Rota de começo
@crismando_bp.route("/inicio", methods=["GET"])
@login_required
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

    # Subquery para contar presenças, faltas e justificadas
    subquery_frequencias = db.session.query(
        Frequencias.fk_id_crismando,
        sa.func.count(sa.case((Frequencias.status_frequencia == 'presente', 1))).label(
            'total_presencas'),
        sa.func.count(sa.case((Frequencias.status_frequencia == 'falta', 1))).label(
            'total_faltas'),
        sa.func.count(sa.case((Frequencias.status_frequencia == 'justificada', 1))).label(
            'total_justificadas')
    ).group_by(Frequencias.fk_id_crismando).subquery()

    # Join com Catequistas e Frequências
    query = db.session.query(
        Crismandos,
        Catequistas,
        Grupos,
        subquery_frequencias.c.total_presencas,
        subquery_frequencias.c.total_faltas,
        subquery_frequencias.c.total_justificadas
    ).join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista
           ).join(Grupos, Catequistas.fk_id_grupo == Grupos.id_grupo
                  ).outerjoin(subquery_frequencias, Crismandos.id == subquery_frequencias.c.fk_id_crismando)

    # Join entre as tabelas Crismandos e Catequistas
    # query = db.session.query(Crismandos, Catequistas).join(Catequistas)

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
                           status_crismando=status_filter,
                           status_filter=status_filter,
                           filtrar_batizado=filtrar_batizado,
                           filtrar_eucaristia=filtrar_eucaristia)


# Rota para editar informações dos crismandos
@crismando_bp.route("/editar_informacoes/<int:id_crismando>", methods=['POST', 'GET'])
@login_required
def editar_infor(id_crismando):

    origem_url_voltar = request.args.get('origem') or request.referrer or url_for(
        'crismando.index')  # Padrão: index

    # Obtendo os dados associados ao id do crismando
    crismando = db.session.query(Crismandos).filter_by(id=id_crismando).first()
    # lista_catequistas = db.session.query(Catequistas).options(joinedload(Catequistas.grupo)).all()
    # lista_catequistas = db.session.query(Catequistas)

    lista_catequistas = db.session.query(
        Catequistas, Grupos).join(Grupos).all()

    if not crismando:
        return "Crismando não encontrado", 404

    return render_template('infor_crismandos.html',
                           crismando=crismando,
                           lista_catequistas=lista_catequistas,
                           origem_url_voltar=origem_url_voltar)


# Rota para salvar alterações nas informações dos crismandos
@crismando_bp.route("/atualizar_informacoes", methods=['POST', ])
@login_required
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


@crismando_bp.route('/geral_crismandos', methods=['POST', 'GET'])
@login_required
@coordenador_required
def geral_crismandos():
    origem_url_voltar = request.args.get('origem') or request.referrer or url_for(
        'crismando.index')  # Padrão: index
    # Obter os valores de busca da URL que vem da pagina index.html
    search_term = request.args.get('busca', '').strip()
    status_filter = request.args.get(
        'buscar_status_crismando', '').strip()  # obtém o status selecionado
    grupo_filtro = request.args.get('buscar_grupo')

    # Pega o valor se o checkbox foi marcado
    filtrar_batizado = request.args.get('batismo')

    # Pega o valor se o checkbox foi marcado
    filtrar_eucaristia = request.args.get('eucaristia')

    # Subquery para contar presenças, faltas e justificadas
    subquery_frequencias = db.session.query(
        Frequencias.fk_id_crismando,
        sa.func.count(sa.case((Frequencias.status_frequencia == 'presente', 1))).label(
            'total_presencas'),
        sa.func.count(sa.case((Frequencias.status_frequencia == 'falta', 1))).label(
            'total_faltas'),
        sa.func.count(sa.case((Frequencias.status_frequencia == 'justificada', 1))).label(
            'total_justificadas')
    ).group_by(Frequencias.fk_id_crismando).subquery()

    # Join com Catequistas e Frequências
    query = db.session.query(
        Crismandos,
        Catequistas,
        Grupos,
        subquery_frequencias.c.total_presencas,
        subquery_frequencias.c.total_faltas,
        subquery_frequencias.c.total_justificadas
    ).join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista
           ).join(Grupos, Catequistas.fk_id_grupo == Grupos.id_grupo
                  ).outerjoin(subquery_frequencias, Crismandos.id == subquery_frequencias.c.fk_id_crismando)

    # Join entre as tabelas Crismandos e Catequistas
    # query = db.session.query(Crismandos, Catequistas).join(Catequistas)

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

    if grupo_filtro:
        query = query.filter(Grupos.id_grupo == grupo_filtro)

    # Ordenação alfabética dos resultados
    query = query.order_by(Crismandos.nome)

    # Obtendo todos os grupos disponíveis
    # grupos_disponiveis = db.session.query(Grupos.nome_grupo).distinct().all()
    grupos_disponiveis = db.session.query(Grupos).all()
    # Assim, no template você terá acesso a grupo.id_grupo e grupo.nome_grupo, como espera.

    # Executamos a consulta e pegamos os resultados
    lista_crismandos = query.all()

    return render_template('geral_crismandos.html',
                           lista_crismandos=lista_crismandos,
                           search_term=search_term,
                           # Garantindo a persistência dos filtros de Batismo e Eucaristia
                           status_crismando=status_filter,
                           status_filter=status_filter,
                           filtrar_batizado=filtrar_batizado,
                           filtrar_eucaristia=filtrar_eucaristia,
                           grupos_disponiveis=grupos_disponiveis,
                           origem_url_voltar=origem_url_voltar)
