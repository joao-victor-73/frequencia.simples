from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy.orm import joinedload
from models.models import Catequistas, Grupos, Crismandos
from flask_login import login_required
from utils.decorators import coordenador_required
from models import db


# Criação do Blueprint
grupos_bp = Blueprint('grupo_bp', __name__)  # nome do blueprint


@grupos_bp.route('/cadastrar_grupo', methods=['POST', 'GET'])
@login_required
@coordenador_required
def cadastrar_grupo():
    from_catequista = request.args.get("from_catequista")

    if request.method == 'POST':
        nome_grupo = request.form['nome_grupo'].strip().title()
        horario = request.form['horario']
        local = request.form['local']
        descricao = request.form['descricao']

        if Grupos.query.filter_by(nome_grupo=nome_grupo).first():
            flash("Este grupo já existe!", "warning")
            return redirect(url_for('grupo.cadastrar_grupo', from_catequista=from_catequista))

        novo_grupo = Grupos(
            nome_grupo=nome_grupo,
            horario=horario,
            local_grupo=local,
            descricao=descricao
        )
        try:
            db.session.add(novo_grupo)
            db.session.commit()
            flash("Grupo criado com sucesso!", "success")

            # Redireciona de volta para a tela de catequista, já com o grupo preenchido
            if from_catequista:
                return redirect(url_for('catequista.cadastrar_catequista_com_grupo', grupo_id=novo_grupo.id_grupo))

            return redirect(url_for('grupo.listar_grupos'))

        except Exception as e:
            db.session.rollback()
            flash("Erro ao salvar o grupo.", "danger")

    return render_template('cadastrar_grupo.html')


# Rota para exibir os grupos de crisma
@grupos_bp.route("/grupos_crisma", methods=['GET', 'POST'])
@login_required
def grupos_crisma():
    # Query para coletar informações de todos os grupos e os catequistas ligados aos grupos
    # infor_grupos = Catequistas.query.join(Grupos, Catequistas.fk_id_grupo == Grupos.id_grupo).all()
    # return render_template('grupos_de_crisma.html', infor_grupos=infor_grupos)

    grupos = Grupos.query.options(
        joinedload(Grupos.catequistas),
        joinedload(Grupos.crismandos)
    ).filter(Grupos.status_informacoes == 1).all()

    """
    Essa instrução acima diz basicamente o seguinte:
        "Quando você buscar os grupos, traga também os crismandos relacionados e os catequistas também,
        tudo em uma única query usando JOIN."

    O joinedload faz o SQLAlchemy gerar uma única query com JOIN que traga todos os relacionamentos desejados
    entre tabelas (desde que tenham sido especificados no relacionamento (backref)).
    """

    return render_template('grupos_de_crisma.html', grupos=grupos)


# Rota para editar informações de grupos de crisma
@grupos_bp.route("/editar_grupo_crisma/int:<grupo_id>", methods=['POST', 'GET'])
@login_required
@coordenador_required
def editar_grupo(grupo_id):

    origem_url_voltar = request.args.get('origem') or request.referrer or url_for(
        'grupo_bp.grupos_crisma')  # Padrão é a lista de grupos

    # Pega o grupo requisitado (fornecido através do grupo_id)
    grupo_requisitado = db.session.query(
        Grupos).filter_by(id_grupo=grupo_id).first()

    # Pega os catequistas vinculados a esse grupo
    lista_catequistas_responsaveis = db.session.query(
        Catequistas).filter_by(fk_id_grupo=grupo_id).filter(Catequistas.status_informacoes == 1).all()

    if not grupo_requisitado:
        return "Grupo não foi encontrado", 404

    # Aqui buscamos TODOS os catequistas
    todos_catequistas = Catequistas.query.filter(Catequistas.status_informacoes == 1).all()

    return render_template("infor_grupo.html",
                           grupo_requisitado=grupo_requisitado,
                           lista_catequistas_responsaveis=lista_catequistas_responsaveis,
                           todos_catequistas=todos_catequistas,
                           origem_url_voltar=origem_url_voltar)


@grupos_bp.route("/atualizar_info_grupo", methods=['POST'])
@login_required
@coordenador_required
def atualizar_info_grupo():
    grupo_id = request.form['grupo_id']
    atualiza_grupo = Grupos.query.filter_by(id_grupo=grupo_id).first()

    if not atualiza_grupo:
        return "Grupo não encontrado", 404

    atualiza_grupo.nome_grupo = request.form['nome_grupo']
    atualiza_grupo.local_grupo = request.form['local_grupo']
    atualiza_grupo.horario = request.form['horario']
    atualiza_grupo.descricao = request.form['descricao']

    try:
        db.session.add(atualiza_grupo)
        db.session.commit()
    except Exception as e:
        print("Erro ao salvar no banco de dados: ", str(e))
        db.session.rollback()

    flash("Informações do grupo atualizadas com sucesso!", "success")
    return redirect(url_for("grupo_bp.editar_grupo", grupo_id=grupo_id))


@grupos_bp.route("/atualizar_catequistas_grupo", methods=['POST'])
@login_required
@coordenador_required
def atualizar_catequistas_grupo():
    grupo_id = request.form['grupo_id']
    grupo = Grupos.query.get(grupo_id)

    if not grupo:
        return "Grupo não encontrado", 404

    # Remove vínculos anteriores
    Catequistas.query.filter_by(fk_id_grupo=grupo_id).update({Catequistas.fk_id_grupo: None})

    # Adiciona os novos
    ids_catequistas = request.form.getlist("catequistas_selecionados")
    for id_cat in ids_catequistas:
        catequista = Catequistas.query.get(int(id_cat))
        if catequista:
            catequista.fk_id_grupo = grupo_id

    db.session.commit()
    flash("Catequistas do grupo atualizados com sucesso!", "success")
    return redirect(url_for("grupo_bp.editar_grupo", grupo_id=grupo_id))



@grupos_bp.route('/deletar_grupo/<int:id_grupo>', methods=['POST', 'GET'])
@coordenador_required
@login_required
def deletar_grupo(id_grupo):

    grupo = Grupos.query.get_or_404(id_grupo)

    grupo.status_informacoes = 0
    db.session.commit()

    flash("Informações da turma foram deletadas com sucesso!", 'success')
    return redirect(url_for('grupo_bp.grupos_crisma'))