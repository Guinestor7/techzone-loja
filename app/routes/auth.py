from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
import re

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('loja.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('conta/login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_senha(senha):
            login_user(user)
            flash(f'Bem-vindo de volta, {user.nome}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('loja.index'))
        else:
            flash('Email ou senha incorretos.', 'danger')

    return render_template('conta/login.html')


@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('loja.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        cpf = request.form.get('cpf', '')
        telefone = request.form.get('telefone', '')

        # Validações básicas
        if not nome or not email or not senha:
            flash('Por favor, preencha todos os campos obrigatórios.', 'warning')
            return render_template('conta/registro.html')

        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'warning')
            return render_template('conta/registro.html')

        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('conta/registro.html')

        # Validar email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Email inválido.', 'danger')
            return render_template('conta/registro.html')

        # Verifica se o email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'warning')
            return render_template('conta/registro.html')

        # Cria novo usuário
        user = User(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=telefone
        )
        user.set_senha(senha)

        db.session.add(user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('conta/registro.html')


@bp.route('/logout')
@login_required
def logout():
    """Faz logout do usuário"""
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('loja.index'))


@bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil do usuário"""
    from app.models import Pedido
    return render_template('conta/perfil.html', Pedido=Pedido)


@bp.route('/pedidos')
@login_required
def pedidos():
    """Lista de pedidos do usuário"""
    from app.models import Pedido
    page = request.args.get('page', 1, type=int)
    pedidos = current_user.pedidos.order_by(Pedido.criado_em.desc()).paginate(page=page, per_page=10)
    return render_template('conta/pedidos.html', pedidos=pedidos)


@bp.route('/enderecos')
@login_required
def enderecos():
    """Lista de endereços do usuário"""
    enderecos = current_user.enderecos.all()
    return render_template('conta/enderecos.html', enderecos=enderecos)
