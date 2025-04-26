from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models.models import Usuarios, Catequistas, Grupos
from utils.decorators import coordenador_required
from models import db


# Criação do Blueprint
auth_bp = Blueprint('auth', __name__)  # nome do blueprint


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuarios.query.filter_by(email=email).first()
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            flash("Login realizado com sucesso", "success")

            return redirect(url_for('crismando.index'))
        else:
            flash('Email ou senha incorretos!', 'danger')

    return render_template('login.html')


@auth_bp.route('/registrar_catequista', methods=['GET', 'POST'])
@login_required
@coordenador_required
def registro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        id_catequista = request.form['fk_id_catequista']

        # Lógica para verificar se o e-mail está cadastrado.
        if Usuarios.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'warning')

        # Lógica para verificar se o catequista ja possui cadastro.
        elif Usuarios.query.filter_by(fk_id_catequista=id_catequista).first():
            flash('Este catequista já possui um usuário!', 'warning')
        else:
            novo_usuario = Usuarios(
                email=email, fk_id_catequista=id_catequista)

            novo_usuario.set_password(senha)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

    catequistas = Catequistas.query.with_entities(
        Catequistas.id_catequista, Catequistas.nome).all()
    return render_template('register.html', catequistas=catequistas)


@auth_bp.route('/registrar_novo_catequista', methods=['POST', 'GET'])
@login_required
@coordenador_required
def register_new_cat():
    if request.method == 'POST':
        nome = request.form['nome'].strip().title()
        data_nascimento = request.form['data_nascimento']
        tel1 = request.form['tel1']
        endereco = request.form['endereco']
        fk_id_grupo = request.form['selecionar_grupo'] or None

        print("Coletando os dados do forms")
        print("Grupo selecionado:", fk_id_grupo)

        if not fk_id_grupo:
            fk_id_grupo = None

        # Verificar se já existe um catequista com o mesmo nome
        if Catequistas.query.filter_by(nome=nome).first():
            flash(f"O catequista '{nome}' já está cadastrado!", "warning")
            return redirect(url_for("catequista.cadastrar_catequista"))

        else:
            novo_catequista = Catequistas(
                nome=nome,
                data_nascimento=data_nascimento,
                tel1=tel1,
                endereco=endereco,
                fk_id_grupo=fk_id_grupo
            )

            try:
                db.session.add(novo_catequista)
                db.session.commit()
                print(novo_catequista)
                print(f"Catequista {nome} registrado com sucesso.")
                flash("Cadastro realizado com sucesso", "success")

            except Exception as e:
                print("Erro ao salvar no banco de dados: ", str(e))
                db.session.rollback()

    # Busca todos os grupos disponíveis para exibir no select
    grupos_disponiveis = Grupos.query.all()

    return render_template('registrar_novo_catequista.html', grupos=grupos_disponiveis)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
