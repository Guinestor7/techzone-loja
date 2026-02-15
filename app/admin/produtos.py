from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models import Produto, Categoria
from app.utils.decorators import admin_required

bp = Blueprint('admin_produtos', __name__)


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
@login_required
@admin_required
def index():
    """Dashboard admin - lista de produtos"""
    produtos = Produto.query.order_by(Produto.criado_em.desc()).all()
    return render_template('admin/dashboard.html', produtos=produtos)


# ==================== PRODUTOS ====================

@bp.route('/produtos')
@login_required
@admin_required
def listar():
    """Lista todos os produtos"""
    page = request.args.get('page', 1, type=int)
    produtos = Produto.query.order_by(Produto.criado_em.desc()).paginate(
        page=page, per_page=20
    )
    return render_template('admin/produtos/listar.html', produtos=produtos)


@bp.route('/produtos/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def criar():
    """Cria um novo produto"""
    if request.method == 'POST':
        # Processa upload da imagem
        imagem = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Adiciona timestamp para evitar duplicatas
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"

                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem = filename

        # Cria o produto
        produto = Produto(
            nome=request.form.get('nome'),
            slug=request.form.get('nome', '').lower().replace(' ', '-').replace('/', '-'),
            descricao=request.form.get('descricao'),
            preco=float(request.form.get('preco', 0)),
            preco_antigo=float(request.form.get('preco_antigo')) if request.form.get('preco_antigo') else None,
            estoque=int(request.form.get('estoque', 0)),
            categoria_id=int(request.form.get('categoria_id')),
            imagem=imagem,
            ativo=request.form.get('ativo') == 'on'
        )

        db.session.add(produto)
        db.session.commit()

        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('admin_produtos.listar'))

    categorias = Categoria.query.all()
    return render_template('admin/produtos/criar.html', categorias=categorias)


@bp.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    """Edita um produto"""
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        # Processa upload da imagem se houver
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                # Remove imagem antiga se existir
                if produto.imagem:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], produto.imagem)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"

                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                produto.imagem = filename

        # Atualiza dados
        produto.nome = request.form.get('nome')
        produto.slug = request.form.get('nome', '').lower().replace(' ', '-').replace('/', '-')
        produto.descricao = request.form.get('descricao')
        produto.preco = float(request.form.get('preco', 0))
        produto.preco_antigo = float(request.form.get('preco_antigo')) if request.form.get('preco_antigo') else None
        produto.estoque = int(request.form.get('estoque', 0))
        produto.categoria_id = int(request.form.get('categoria_id'))
        produto.ativo = request.form.get('ativo') == 'on'

        db.session.commit()

        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos.listar'))

    categorias = Categoria.query.all()
    return render_template('admin/produtos/editar.html', produto=produto, categorias=categorias)


@bp.route('/produtos/deletar/<int:id>', methods=['POST'])
@login_required
@admin_required
def deletar(id):
    """Deleta um produto"""
    produto = Produto.query.get_or_404(id)

    # Remove imagem se existir
    if produto.imagem:
        imagem_path = os.path.join(current_app.config['UPLOAD_FOLDER'], produto.imagem)
        if os.path.exists(imagem_path):
            os.remove(imagem_path)

    db.session.delete(produto)
    db.session.commit()

    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('admin_produtos.listar'))


# ==================== CATEGORIAS ====================

@bp.route('/categorias')
@login_required
@admin_required
def categorias():
    """Lista todas as categorias"""
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('admin/categorias/listar.html', categorias=categorias)


@bp.route('/categorias/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def criar_categoria():
    """Cria uma nova categoria"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        slug = request.form.get('slug')
        descricao = request.form.get('descricao')

        # Verifica se o slug já existe
        if Categoria.query.filter_by(slug=slug).first():
            flash('Este slug já está em uso.', 'warning')
            return render_template('admin/categorias/criar.html')

        categoria = Categoria(
            nome=nome,
            slug=slug,
            descricao=descricao
        )

        db.session.add(categoria)
        db.session.commit()

        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('admin_produtos.categorias'))

    return render_template('admin/categorias/criar.html')


@bp.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_categoria(id):
    """Edita uma categoria"""
    categoria = Categoria.query.get_or_404(id)

    if request.method == 'POST':
        nome = request.form.get('nome')
        slug = request.form.get('slug')
        descricao = request.form.get('descricao')

        # Verifica se o slug já existe (exceto para esta categoria)
        existing = Categoria.query.filter_by(slug=slug).first()
        if existing and existing.id != categoria.id:
            flash('Este slug já está em uso.', 'warning')
            return render_template('admin/categorias/editar.html', categoria=categoria)

        categoria.nome = nome
        categoria.slug = slug
        categoria.descricao = descricao

        db.session.commit()

        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('admin_produtos.categorias'))

    return render_template('admin/categorias/editar.html', categoria=categoria)


@bp.route('/categorias/deletar/<int:id>', methods=['POST'])
@login_required
@admin_required
def deletar_categoria(id):
    """Deleta uma categoria"""
    categoria = Categoria.query.get_or_404(id)

    # Verifica se há produtos nesta categoria
    if categoria.produtos.count() > 0:
        flash('Não é possível deletar uma categoria que possui produtos.', 'danger')
        return redirect(url_for('admin_produtos.categorias'))

    db.session.delete(categoria)
    db.session.commit()

    flash('Categoria deletada com sucesso!', 'success')
    return redirect(url_for('admin_produtos.categorias'))
