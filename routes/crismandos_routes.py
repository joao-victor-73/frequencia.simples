from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.models import Usuarios, Catequistas, Crismandos, Grupos, Frequencias, InforFrequencias
from flask_login import login_required, current_user
from utils.decorators import coordenador_required
from models import db
import sqlalchemy as sa


# Criação do Blueprint
crismando_bp = Blueprint('crismando_bp', __name__)  # nome do blueprint


# Rota de começo
@crismando_bp.route("/lista_de_crismandos", methods=["GET"])
@login_required
def lista_de_crismandos():
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
        Grupos,
        subquery_frequencias.c.total_presencas,
        subquery_frequencias.c.total_faltas,
        subquery_frequencias.c.total_justificadas
    ).join(Grupos, Crismandos.fk_id_grupo == Grupos.id_grupo
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

    # lista_catequistas = db.session.query(Catequistas).filter_by(fk_id_grupo=crismando.fk_id_grupo).all()

    # Pega os catequistas do grupo do crismando
    catequistas_do_grupo = db.session.query(Catequistas).filter_by(fk_id_grupo=crismando.fk_id_grupo).all()

    # Se for coordenador, envia a lista de todos os grupos também
    lista_grupos = []
    if current_user.catequista.nivel == 'coordenador':
        lista_grupos = Grupos.query.all()

    if not crismando:
        return "Crismando não encontrado", 404

    return render_template('infor_crismandos.html',
                           crismando=crismando,
                           catequistas_do_grupo=catequistas_do_grupo,
                           lista_grupos=lista_grupos,
                           origem_url_voltar=origem_url_voltar)


# Rota para salvar alterações nas informações dos crismandos
@crismando_bp.route("/atualizar_informacoes", methods=['POST', ])
@login_required
def atualizar_infor():

    # Pega o id do crismando. (esse id vem de um input hidden la no template 'infor_crismandos')
    atualiza_crismando = Crismandos.query.filter_by(id=request.form['id_crismando']).first()

    atualiza_crismando.nome = request.form['nome_crismando']
    atualiza_crismando.data_nascimento = request.form['data_nascimento']
    atualiza_crismando.tel1 = request.form['telefone1']
    atualiza_crismando.tel2 = request.form['telefone2']
    atualiza_crismando.nome_mae = request.form['nome_mae']
    atualiza_crismando.nome_pai = request.form['nome_pai']
    atualiza_crismando.nome_padrim = request.form['nome_padrim']
    atualiza_crismando.endereco = request.form['endereco']
    atualiza_crismando.cidade = request.form['cidade']
    atualiza_crismando.status_crismando = request.form['status_crismando']
    atualiza_crismando.batismo = request.form['batismo']
    atualiza_crismando.eucaristia = request.form['eucaristia']
    atualiza_crismando.estado_civil = request.form['estado_civil']
    atualiza_crismando.possui_filhos = request.form['possui_filhos']
    atualiza_crismando.possui_deficiencia = request.form['possui_deficiencia']

    # Se for coordenador, atualiza também o grupo
    if current_user.catequista.nivel == 'coordenador':
        atualiza_crismando.fk_id_grupo = request.form['grupo_id']

    try:
        db.session.add(atualiza_crismando)
        db.session.commit()
    except Exception as e:
        print("Erro ao salvar no banco de dados: ", str(e))
        db.session.rollback()

    return redirect(url_for('crismando_bp.lista_de_crismandos'))


@crismando_bp.route('/geral_crismandos', methods=['POST', 'GET'])
@login_required
@coordenador_required
def geral_crismandos():
    # Obter os valores de busca da URL que vem da pagina index.html
    origem_url_voltar = request.args.get('origem') or request.referrer or url_for('crismando.index')  # Padrão: index
    
    search_term = request.args.get('busca', '').strip()
    status_filter = request.args.get('buscar_status_crismando', '').strip()  # obtém o status selecionado
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
        Grupos,
        subquery_frequencias.c.total_presencas,
        subquery_frequencias.c.total_faltas,
        subquery_frequencias.c.total_justificadas
    ).join(Grupos, Crismandos.fk_id_grupo == Grupos.id_grupo
        ).outerjoin(subquery_frequencias, Crismandos.id == subquery_frequencias.c.fk_id_crismando
                    ).filter( Crismandos.status_informacoes == 1)


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


@crismando_bp.route('/registrar_crismando', methods=['POST', 'GET'])
@login_required
def registrar_crismando():
    grupos_disponiveis = db.session.query(Grupos).all()
    catequistas_disponiveis = db.session.query(Catequistas).all()

    return render_template('registrar_crismando.html',
                           grupos_disponiveis=grupos_disponiveis,
                           catequistas_disponiveis=catequistas_disponiveis)



@crismando_bp.route('/salvar_crismando', methods=['POST', 'GET'])
@login_required
def salvar_crismando():
    if request.method == 'POST':
        nome = request.form['nome'].strip().title()
        nome_mae = request.form['nome_mae'].strip().title()
        nome_pai = request.form['nome_pai'].strip().title()
        data_nascimento = request.form['data_nascimento']
        tel1 = request.form['tel1']
        tel2 = request.form['tel2']
        endereco = request.form['endereco']
        cidade = request.form['cidade']
        fk_id_grupo = request.form['fk_id_grupo']
        batismo = request.form['batismo']
        eucaristia = request.form['eucaristia']
        estado_civil = request.form['estado_civil']
        possui_filhos = request.form['possui_filhos']

        possui_deficiencia = request.form['possui_deficiencia']
        if possui_deficiencia == 'sim':
            descricao = request.form.get('descricao_deficiencia', '').strip()
            possui_deficiencia = descricao or 'sim'
        else:
            possui_deficiencia = 'nao'

        if Crismandos.query.filter_by(nome=nome).first():
            flash(f"O Crismando '{nome}' já está cadastrado!", "warning")
            return redirect(url_for("crismando_bp.lista_de_crismandos"))
        
        else:
            novo_crismando = Crismandos(
                nome=nome,
                nome_pai=nome_pai,
                nome_mae=nome_mae,
                data_nascimento=data_nascimento,
                tel1=tel1,
                tel2=tel2,
                endereco=endereco,
                cidade=cidade,
                fk_id_grupo=fk_id_grupo,
                batismo=batismo,
                eucaristia=eucaristia,
                estado_civil=estado_civil,
                possui_filhos=possui_filhos,
                possui_deficiencia=possui_deficiencia
            )

            try:
                db.session.add(novo_crismando)
                db.session.commit()
                print(novo_crismando)
                print(f"Novo crismando: {nome}, foi registrado com sucesso.")
                flash("Cadastro realizado com sucesso", "success")
            
            except Exception as e:
                print("Erro ao salvar no banco de dados: ", str(e))
                db.session.rollback()

    return redirect(url_for('crismando_bp.lista_de_crismandos'))


@crismando_bp.route('/deletar_crismando/<int:id>', methods=['POST', 'GET'])
@login_required
def deletar_crismando(id):

    crismando = Crismandos.query.get_or_404(id)

    crismando.status_informacoes = 0
    db.session.commit()

    flash("Informações do crismando deletada com sucesso!", 'success')
    return redirect(url_for('crismando_bp.lista_de_crismandos'))