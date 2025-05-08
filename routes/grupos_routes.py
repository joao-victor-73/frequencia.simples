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
    ).all()

    """
    Essa instrução acima diz basicamente o seguinte:
        "Quando você buscar os grupos, traga também os crismandos relacionados e os catequistas também,
        tudo em uma única query usando JOIN."

    O joinedload faz o SQLAlchemy gerar uma única query com JOIN que traga todos os relacionamentos desejados
    entre tabelas (desde que tenham sido especificados no relacionamento (backref)).
    """

    return render_template('grupos_de_crisma.html', grupos=grupos)


# Rota para editar informações de grupos de crisma
@grupos_bp.route("/editar_grupo_crisma/int:<id_grupo>", methods=['POST', 'GET'])
@login_required
@coordenador_required
def editar_grupo(id_grupo):
    pass
