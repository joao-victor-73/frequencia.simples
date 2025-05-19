from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.models import Catequistas, Crismandos, Grupos, Frequencias, InforFrequencias, FrequenciaCatequistas, PresencaCatequista
from flask_login import login_required, current_user
from utils.decorators import coordenador_required
from models import db
from datetime import datetime


# Criação do Blueprint
frequencias_bp = Blueprint('frequencia_bp', __name__)  # nome do blueprint


# Rota para exibir o formulário de frequência
@frequencias_bp.route("/fazer_frequencia", methods=["GET"])
@login_required
def fazer_frequencia():
    # crismando = db.session.query(Crismandos).filter_by(id=id_crismando).first()
    # lista_crismandos = Crismandos.query.filter_by(status_crismando='ativo').all()

    # Vai pegar o usuário logado e trazer a informação de qual grupo ele é responsável
    grupo_do_catequista = current_user.catequista.grupo

    grupo_id = grupo_do_catequista.id_grupo

    # Buscar crismandos ativos do grupo
    lista_crismandos = Crismandos.query\
        .filter_by(fk_id_grupo=grupo_id, status_crismando='ativo').order_by(Crismandos.nome).all()

    return render_template('fazer_frequencia.html', lista_crismandos=lista_crismandos)


# Rota para salvar a frequência no banco
@frequencias_bp.route("/salvar_frequencia", methods=["GET", "POST"])
@login_required
def salvar_frequencia():
    if request.method == 'POST':
        grupo_catequista = current_user.catequista.grupo

        titulo = request.form.get('titulo_encontro')
        data_chamada = request.form.get('data_chamada')

        # Criar registro em InforFrequencias
        nova_info_freq = InforFrequencias(titulo_encontro=titulo,
                                          data_chamada=datetime.strptime(
                                              data_chamada, '%Y-%m-%d'),
                                          fk_id_catequista=current_user.catequista.id_catequista
                                          )
        db.session.add(nova_info_freq)
        db.session.commit()

        id_infor_freq = nova_info_freq.id_infor_freq

        lista_crismandos = db.session.query(Crismandos)\
            .join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista)\
            .filter(Crismandos.status_crismando == 'ativo')\
            .filter(Catequistas.grupo == grupo_catequista).all()

        for crismando in lista_crismandos:
            status = 'presente'
            observacao = request.form.get(f'observacao_{crismando.id}', None)

            if observacao:
                status = 'justificada'
            elif request.form.get(f'faltou_{crismando.id}'):
                status = 'falta'

            nova_frequencia = Frequencias(
                status_frequencia=status,
                observacao=observacao,
                fk_id_crismando=crismando.id,
                fk_id_infor_freq=id_infor_freq
            )
            db.session.add(nova_frequencia)

        db.session.commit()
        flash("Frequencias registradas com sucesso!", "success")

        return redirect(url_for('frequencia.listar_frequencias'))


# Rota para listar frequências registradas
@frequencias_bp.route('/listar_frequencias')
@login_required
def listar_frequencias():
    data_filtro = request.args.get('data_filtro')
    titulo_filtro = request.args.get('busca_titulo')

    id_grupo_usuario = current_user.catequista.fk_id_grupo
    id_catequista = current_user.catequista.id_catequista

    # Base da consulta SEM filtro por catequista ainda
    query = db.session.query(InforFrequencias).distinct()\
        .join(Frequencias, InforFrequencias.id_infor_freq == Frequencias.fk_id_infor_freq)\
        .join(Crismandos, Frequencias.fk_id_crismando == Crismandos.id)\
        .join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista)\
        .filter(Catequistas.fk_id_grupo == id_grupo_usuario)\
        .filter(InforFrequencias.fk_id_catequista == id_catequista)

    """
    # Catequista comum: restringe à sua autoria
    query = query.filter(Catequistas.fk_id_grupo == id_grupo_usuario)
    query = query.filter(InforFrequencias.fk_id_catequista ==
                         current_user.catequista.id_catequista)
    """

    # Filtro por data
    if data_filtro:
        try:
            data_formatada = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(
                InforFrequencias.data_chamada == data_formatada)
        except ValueError:
            flash("Formato de data inválido!", "danger")

    # Filtro por título
    if titulo_filtro:
        query = query.filter(
            InforFrequencias.titulo_encontro.ilike(f"%{titulo_filtro}%"))

    registros_de_frequencias = query.order_by(
        InforFrequencias.data_chamada.desc()).all()

    return render_template('historico_frequencias.html',
                           registros=registros_de_frequencias,
                           data_filtro=data_filtro,
                           titulo_filtro=titulo_filtro,
                           grupo_catequista=current_user.catequista.grupo)


@frequencias_bp.route('/geral_frequencias', methods=['GET'])
@login_required
@coordenador_required
def geral_frequencias():
    if current_user.catequista.nivel != 'coordenador':
        flash("Acesso restrito!", "danger")
        return redirect(url_for('frequencia.listar_frequencias'))

    grupo_filtro = request.args.get('grupo_filtro')
    data_filtro = request.args.get('data_filtro')
    titulo_filtro = request.args.get('busca_titulo')

    # Debug: Verificando valor do filtro
    print(f"grupo_filtro: {grupo_filtro}")

    # Junção entre InforFrequencias, Catequistas e Grupos
    query = db.session.query(InforFrequencias).distinct().join(
        Catequistas, InforFrequencias.fk_id_catequista == Catequistas.id_catequista
    ).join(
        Grupos, Catequistas.fk_id_grupo == Grupos.id_grupo  # Junção com a tabela Grupos
    )

    # Filtro por grupo
    if grupo_filtro:
        # Debug: Verificando filtro aplicado
        print(f"Aplicando filtro de grupo: {grupo_filtro}")
        query = query.filter(Grupos.nome_grupo == grupo_filtro)

    # Filtro por data
    if data_filtro:
        try:
            data_formatada = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(
                InforFrequencias.data_chamada == data_formatada)
        except ValueError:
            flash("Formato de data inválido!", "danger")

    # Filtro por título
    if titulo_filtro:
        query = query.filter(
            InforFrequencias.titulo_encontro.ilike(f"%{titulo_filtro}%"))

    # Obtendo os registros filtrados
    registros = query.order_by(InforFrequencias.data_chamada.desc()).all()

    # Obtendo todos os grupos disponíveis
    grupos_disponiveis = db.session.query(Grupos.nome_grupo).distinct().all()

    # Debug: Verificando quantidade de registros
    print(f"Quantidade de registros: {len(registros)}")

    # Renderizando o template
    return render_template('frequencias_gerais.html',
                           registros=registros,
                           grupos_disponiveis=grupos_disponiveis,
                           grupo_filtro=grupo_filtro,
                           data_filtro=data_filtro,
                           titulo_filtro=titulo_filtro)


@frequencias_bp.route('/listar_frequencias/<int:id>', methods=['GET'])
@login_required
def detalhes_frequencia(id):
    id_grupo_usuario = current_user.catequista.fk_id_grupo
    origem_url_voltar = request.args.get('origem') or request.referrer or url_for(
        'listar_frequencias')  # Padrão: listar_frequencias

    frequencia = InforFrequencias.query.get(id)
    if not frequencia:
        return "Frequência não encontrada", 404

    # Verifica se há algum crismando desse grupo vinculado a essa frequência
    autorizada = db.session.query(Frequencias)\
        .join(Crismandos, Frequencias.fk_id_crismando == Crismandos.id)\
        .join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista)\
        .filter(Frequencias.fk_id_infor_freq == id)\
        .filter(Catequistas.fk_id_grupo == id_grupo_usuario).first()

    if not autorizada:
        flash("Você não tem permissão para acessar essa chamada.", "danger")
        return redirect(url_for('frequencia.listar_frequencias'))

    # Buscar todos os registros dessa chamada, mas apenas do grupo do usuário
    registros = db.session.query(Frequencias)\
        .join(Crismandos, Frequencias.fk_id_crismando == Crismandos.id)\
        .join(Catequistas, Crismandos.fk_id_catequista == Catequistas.id_catequista)\
        .filter(Frequencias.fk_id_infor_freq == id)\
        .filter(Catequistas.fk_id_grupo == id_grupo_usuario).all()

    return render_template('detalhes_frequencia.html',
                           frequencia=frequencia,
                           registros=registros,
                           grupo_catequista=current_user.catequista.grupo,
                           origem_url_voltar=origem_url_voltar)




@frequencias_bp.route("/frequencia_catequistas", methods=["GET"])
@login_required
@coordenador_required
def fazer_frequencia_catequistas():

    catequistas = db.session.query(Catequistas).order_by(Catequistas.nome).all()

    catequistas = Catequistas.query.filter(Catequistas.id_catequista != 26).all()


    return render_template("fazer_freq_catequistas.html", 
                           catequistas=catequistas)



@frequencias_bp.route("/salvar_frequencia_catequistas", methods=["POST"])
@login_required
@coordenador_required
def salvar_frequencia_catequistas():
    titulo = request.form.get('titulo_encontro')
    data_encontro = request.form.get('data_chamada')

    nova_info_freq = FrequenciaCatequistas(
        titulo_encontro=titulo,
        data_encontro=datetime.strptime(data_encontro, '%Y-%m-%d')
    )
    db.session.add(nova_info_freq)
    db.session.commit()

    id_infor_freq = nova_info_freq.id_freq_catequista

    lista_catequistas = db.session.query(Catequistas).order_by(Catequistas.nome).all()

    for catequista in lista_catequistas:
        status = 'presente'
        observacao = request.form.get(f'observacao_{catequista.id_catequista}', None)

        if observacao:
            status = 'justificada'
        elif request.form.get(f'faltou_{catequista.id_catequista}'):
            status = 'falta'

        nova_frequencia = PresencaCatequista(
            status_frequencia=status,
            observacao=observacao,
            fk_id_catequista=catequista.id_catequista,
            fk_id_freq_catequista=id_infor_freq
        )
        db.session.add(nova_frequencia)

    db.session.commit()
    flash("Frequência dos catequistas registrada com sucesso!", "success")

    return redirect(url_for("frequencia_bp.listar_frequencias_catequistas"))



@frequencias_bp.route("/listar_frequencias_catequistas", methods=["GET"])
@login_required
@coordenador_required
def listar_frequencias_catequistas():
    data_filtro = request.args.get("data_filtro")
    titulo_filtro = request.args.get("busca_titulo")

    query = db.session.query(FrequenciaCatequistas).order_by(FrequenciaCatequistas.data_encontro.desc())

    if data_filtro:
        try:
            data_formatada = datetime.strptime(data_filtro, "%Y-%m-%d").date()
            query = query.filter(FrequenciaCatequistas.data_encontro == data_formatada)
        except ValueError:
            flash("Formato de data inválido!", "danger")

    if titulo_filtro:
        query = query.filter(FrequenciaCatequistas.titulo_encontro.ilike(f"%{titulo_filtro}%"))

    registros = query.all()

    return render_template("historico_frequencias_catequistas.html",
                           registros=registros,
                           data_filtro=data_filtro,
                           titulo_filtro=titulo_filtro)


@frequencias_bp.route('/detalhar_frequencia_catequistas/<int:id>')
@login_required
@coordenador_required
def detalhar_frequencia_catequistas(id):
    encontro = FrequenciaCatequistas.query.get_or_404(id)
    registros = PresencaCatequista.query.filter_by(fk_id_freq_catequista=id).join(Catequistas).order_by(Catequistas.nome).all()

    return render_template("detalhar_freq_catequistas.html",
                           encontro=encontro,
                           registros=registros)
