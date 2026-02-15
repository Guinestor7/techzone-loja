from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Produto, Categoria

bp = Blueprint('loja', __name__)


@bp.route('/')
def index():
    """Página inicial - produtos em destaque"""
    produtos_destaque = Produto.query.filter_by(ativo=True).order_by(Produto.criado_em.desc()).limit(8).all()
    categorias = Categoria.query.all()
    return render_template('loja/index.html', produtos=produtos_destaque, categorias=categorias)


@bp.route('/produtos')
def produtos():
    """Listagem de produtos com filtros"""
    # Filtros
    categoria_slug = request.args.get('categoria')
    busca = request.args.get('q', '')
    ordenar = request.args.get('ordem', 'novos')

    # Query base
    query = Produto.query.filter_by(ativo=True)

    # Filtro por categoria
    if categoria_slug:
        categoria = Categoria.query.filter_by(slug=categoria_slug).first()
        if categoria:
            query = query.filter_by(categoria_id=categoria.id)

    # Busca por nome
    if busca:
        query = query.filter(Produto.nome.ilike(f'%{busca}%'))

    # Ordenação
    if ordenar == 'preco-asc':
        query = query.order_by(Produto.preco.asc())
    elif ordenar == 'preco-desc':
        query = query.order_by(Produto.preco.desc())
    elif ordenar == 'nome':
        query = query.order_by(Produto.nome.asc())
    else:  # novos
        query = query.order_by(Produto.criado_em.desc())

    # Paginação
    page = request.args.get('page', 1, type=int)
    produtos = query.paginate(page=page, per_page=12)
    categorias = Categoria.query.all()

    return render_template(
        'loja/produtos.html',
        produtos=produtos,
        categorias=categorias,
        categoria_atual=categoria_slug,
        busca=busca,
        ordenar=ordenar
    )


@bp.route('/produto/<slug>')
def produto(slug):
    """Página de detalhes do produto"""
    produto = Produto.query.filter_by(slug=slug, ativo=True).first_or_404()
    # Produtos relacionados da mesma categoria
    relacionados = Produto.query.filter(
        Produto.categoria_id == produto.categoria_id,
        Produto.id != produto.id,
        Produto.ativo == True
    ).limit(4).all()

    return render_template('loja/produto.html', produto=produto, relacionados=relacionados)


@bp.route('/categoria/<slug>')
def categoria(slug):
    """Listagem de produtos por categoria"""
    categoria = Categoria.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    produtos = Produto.query.filter_by(
        categoria_id=categoria.id,
        ativo=True
    ).order_by(Produto.criado_em.desc()).paginate(page=page, per_page=12)

    return render_template('loja/categoria.html', categoria=categoria, produtos=produtos)
