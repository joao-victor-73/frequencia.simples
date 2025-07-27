from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.models import Usuarios, Catequistas, Grupos
from flask_login import login_required
from utils.decorators import coordenador_required
from models import db


# Criação do Blueprint
catequista_bp = Blueprint('catequista_bp', __name__)  # nome do blueprint


@catequista_bp.route('/registrar_novo_catequista_com_grupo', methods=['POST', 'GET'])
@login_required
@coordenador_required
def cadastrar_catequista_com_grupo():
    grupo_id = request.args.get("grupo_id", type=int)
    print(f"ID do grupo: {grupo_id}")

    grupos_disponiveis = Grupos.query.all()
    return render_template('registrar_novo_catequista.html', grupos=grupos_disponiveis, grupo_selecionado=grupo_id)


@catequista_bp.route("/lista_geral_catequistas", methods=["GET", "POST"])
@login_required
@coordenador_required
def geral_catequistas():
    todos_os_catequistas = (
        Catequistas.query
        .join(Grupos, Catequistas.fk_id_grupo == Grupos.id_grupo)
        .filter(Catequistas.status_informacoes == 1)
        .all()
    )

    # for catequista in todos_os_catequistas:
    # print(catequista.nome, catequista.data_nascimento, catequista.tel1, catequista.endereco)

    return render_template('lista_geral_catequistas.html',
                           todos_os_catequistas=todos_os_catequistas)


@catequista_bp.route('/deletar_catequista/<int:id_catequista>', methods=['POST', 'GET'])
@coordenador_required
@login_required
def deletar_catequista(id_catequista):

    catequista = Catequistas.query.get_or_404(id_catequista)

    catequista.status_informacoes = 0
    db.session.commit()

    flash("Informações do catequista deletada com sucesso!", 'success')
    return redirect(url_for('catequista_bp.geral_catequistas'))


@catequista_bp.route("/editar_infor_catequista/<int:id_catequista>", methods=['POST', 'GET'])
@login_required
@coordenador_required
def editar_infor_catequista(id_catequista):

    # Query para obter os dados associados ao id fornecido
    # Query para obter os dados associados ao id fornecido e o join para obter o catequista e seu grupo
    catequista = db.session.query(Catequistas).join(Grupos).filter(
        Catequistas.id_catequista == id_catequista
    ).first()

    # Todos os grupos disponíveis para o dropdown
    todos_grupos = Grupos.query.all()

    if not catequista:
        return "Catequista não encontrado", 404

    return render_template('editar_infor_cateq.html', catequista=catequista, todos_grupos=todos_grupos)


@catequista_bp.route("/salvar_infor_catequista", methods=['POST', 'GET'])
@login_required
@coordenador_required
def salvar_infor_catequista():
    # Pegando o id que vem de um input hidden de dentro do template "editar_infor_cateq.html"
    atualizar_catequista = Catequistas.query.filter_by(
        id_catequista=request.form['id_catequista']).first()

    atualizar_catequista.nome = request.form['nome_catequista']
    atualizar_catequista.data_nascimento = request.form['data_nascimento']
    atualizar_catequista.endereco = request.form['endereco']
    atualizar_catequista.fk_id_grupo = request.form['grupo_responsavel']
    atualizar_catequista.nivel = request.form['nivel']
    atualizar_catequista.tel1 = request.form['tel1']

    try:
        db.session.add(atualizar_catequista)
        db.session.commit()
    except Exception as e:
        print("Erro ao salvar no banco de dados: ", str(e))
        db.session.rollback()

    return redirect(url_for('catequista_bp.geral_catequistas'))

