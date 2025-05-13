import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import db, Catequistas

# Criação do Blueprint
others_bp = Blueprint('other', __name__)  # nome do blueprint


@others_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    # id_catequista = request.args.get('id_catequista')
    # catequista = db.session.query(Catequistas).filter_by(id_catequista=id_catequista).first()
    
    return render_template('perfil.html')


@others_bp.route('/perfil/atualizar', methods=['POST'])
@login_required
def atualizar_perfil():
    nome = request.form.get('nome')
    email = request.form.get('email')
    tel1 = request.form.get('tel1')
    data_nascimento = request.form.get('data_nascimento')
    endereco = request.form.get('endereco')
    avatar_perfil = request.form.get('avatar_perfil')

    # Atualiza dados pessoais
    current_user.email = email
    current_user.catequista.nome = nome
    current_user.catequista.tel1 = tel1
    current_user.catequista.data_nascimento = data_nascimento
    current_user.catequista.endereco = endereco
    current_user.avatar_perfil = avatar_perfil

    """
    # Atualiza imagem (se houver)
    foto = request.files.get('foto')
    if foto and foto.filename:
        filename = secure_filename(foto.filename)
        path = os.path.join(current_app.static_folder, 'uploads', filename)
        foto.save(path)
        current_user.foto = filename
    """

    # Alteração de senha
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')

    if senha_atual or nova_senha or confirmar_senha:
        if not check_password_hash(current_user.senha, senha_atual):
            flash("Senha atual incorreta.", "danger")
            return redirect(url_for('other.perfil'))

        if nova_senha != confirmar_senha:
            flash("As senhas novas não coincidem.", "danger")
            return redirect(url_for('other.perfil'))

        current_user.senha = generate_password_hash(nova_senha)

    # Salva alterações no banco de dados
    db.session.commit()
    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for('other.perfil'))


@others_bp.route("/", methods=["GET"])
def inicio():
    return render_template('inicio.html')


@others_bp.route("/relatar_bug", methods=["GET"])
def relatar_bug():
    return render_template('inicio.html')
