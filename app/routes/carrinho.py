from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.models import Produto

bp = Blueprint('carrinho', __name__)


def _get_carrinho():
    """Retorna o carrinho da sessão"""
    return session.get('carrinho', {})


def _save_carrinho(carrinho):
    """Salva o carrinho na sessão"""
    session['carrinho'] = carrinho
    session.modified = True


@bp.route('/')
def index():
    """Página do carrinho"""
    carrinho = _get_carrinho()
    itens = []
    total = 0

    for produto_id, item in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if produto:
            subtotal = produto.preco * item['quantidade']
            total += subtotal
            itens.append({
                'produto': produto,
                'quantidade': item['quantidade'],
                'subtotal': subtotal
            })

    return render_template('carrinho/index.html', itens=itens, total=total)


@bp.route('/adicionar/<int:produto_id>', methods=['POST'])
def adicionar(produto_id):
    """Adiciona um produto ao carrinho"""
    data = request.get_json() or {}
    quantidade = data.get('quantity', 1)

    produto = Produto.query.get_or_404(produto_id)

    if produto.estoque < quantidade:
        return jsonify({'success': False, 'message': 'Estoque insuficiente'}), 400

    carrinho = _get_carrinho()

    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] += quantidade
    else:
        carrinho[str(produto_id)] = {'quantidade': quantidade}

    _save_carrinho(carrinho)

    return jsonify({'success': True, 'count': _get_carrinho_count()})


@bp.route('/remover/<int:produto_id>', methods=['POST'])
def remover(produto_id):
    """Remove um produto do carrinho"""
    carrinho = _get_carrinho()

    if str(produto_id) in carrinho:
        del carrinho[str(produto_id)]
        _save_carrinho(carrinho)

    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': True, 'count': _get_carrinho_count()})
    return redirect(url_for('carrinho.index'))


@bp.route('/atualizar', methods=['POST'])
def atualizar():
    """Atualiza a quantidade de um item no carrinho"""
    produto_id = request.form.get('produto_id', type=int)
    quantidade = request.form.get('quantidade', type=int, default=1)

    if quantidade < 1:
        return jsonify({'success': False, 'message': 'Quantidade inválida'}), 400

    produto = Produto.query.get_or_404(produto_id)

    if produto.estoque < quantidade:
        return jsonify({'success': False, 'message': 'Estoque insuficiente'}), 400

    carrinho = _get_carrinho()

    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] = quantidade
        _save_carrinho(carrinho)

    return jsonify({'success': True, 'count': _get_carrinho_count()})


@bp.route('/limpar', methods=['POST'])
def limpar():
    """Limpa o carrinho"""
    session.pop('carrinho', None)
    flash('Carrinho limpo com sucesso.', 'info')
    return redirect(url_for('carrinho.index'))


@bp.route('/api/count')
def count():
    """API para retornar a quantidade de itens no carrinho"""
    return jsonify({'count': _get_carrinho_count()})


def _get_carrinho_count():
    """Retorna o total de itens no carrinho"""
    carrinho = _get_carrinho()
    return sum(item['quantidade'] for item in carrinho.values())
