import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import db

# Criação do Blueprint
others_bp = Blueprint('other', __name__)  # nome do blueprint


@others_bp.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')


@others_bp.route("/", methods=["GET"])
def inicio():
    return render_template('inicio.html')


@others_bp.route("/relatar_bug", methods=["GET"])
def relatar_bug():
    return render_template('inicio.html')