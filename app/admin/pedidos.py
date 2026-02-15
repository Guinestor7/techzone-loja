from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Pedido, ItemPedido
from app.utils.decorators import admin_required

bp = Blueprint('admin_pedidos', __name__)


@bp.route('/pedidos')
@login_required
@admin_required
def listar():
    """Lista todos os pedidos para o admin"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')

    query = Pedido.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    pedidos = query.order_by(Pedido.criado_em.desc()).paginate(page=page, per_page=20)

    return render_template('admin/pedidos/listar.html', pedidos=pedidos, status_filter=status_filter)


@bp.route('/pedidos/<int:id>')
@login_required
@admin_required
def detalhar(id):
    """Detalhes de um pedido para o admin"""
    pedido = Pedido.query.get_or_404(id)
    return render_template('admin/pedidos/detalhar.html', pedido=pedido)


@bp.route('/pedidos/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def atualizar_status(id):
    """Atualiza o status de um pedido"""
    pedido = Pedido.query.get_or_404(id)
    novo_status = request.form.get('status')

    status_validos = ['pendente', 'pago', 'enviando', 'entregue', 'cancelado']

    if novo_status not in status_validos:
        flash('Status inválido.', 'danger')
        return redirect(url_for('admin_pedidos.detalhar', id=id))

    pedido.status = novo_status
    db.session.commit()

    flash(f'Status do pedido atualizado para {novo_status}.', 'success')
    return redirect(url_for('admin_pedidos.detalhar', id=id))


@bp.route('/pedidos/<int:id>/enviar', methods=['POST'])
@login_required
@admin_required
def marcar_enviado(id):
    """Marca o pedido como enviado"""
    pedido = Pedido.query.get_or_404(id)

    if pedido.status != 'pago':
        flash('Apenas pedidos pagos podem ser enviados.', 'warning')
        return redirect(url_for('admin_pedidos.detalhar', id=id))

    pedido.status = 'enviando'
    db.session.commit()

    flash('Pedido marcado como enviado!', 'success')
    return redirect(url_for('admin_pedidos.detalhar', id=id))


@bp.route('/pedidos/<int:id>/cancelar', methods=['POST'])
@login_required
@admin_required
def cancelar(id):
    """Cancela um pedido e devolve o estoque"""
    pedido = Pedido.query.get_or_404(id)

    if pedido.status in ['entregue', 'enviando']:
        flash('Não é possível cancelar pedidos enviados ou entregues.', 'warning')
        return redirect(url_for('admin_pedidos.detalhar', id=id))

    # Devolve estoque
    for item in pedido.itens:
        if item.produto:
            item.produto.estoque += item.quantidade

    pedido.status = 'cancelado'
    db.session.commit()

    flash('Pedido cancelado e estoque devolvido.', 'success')
    return redirect(url_for('admin_pedidos.detalhar', id=id))
