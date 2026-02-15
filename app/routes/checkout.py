from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Produto, Pedido, ItemPedido, Endereco

bp = Blueprint('checkout', __name__)


def _get_carrinho():
    """Retorna o carrinho da sessão"""
    return session.get('carrinho', {})


def _clear_carrinho():
    """Limpa o carrinho da sessão"""
    session.pop('carrinho', None)
    session.modified = True


@bp.route('/')
@login_required
def index():
    """Página de checkout"""
    carrinho = _get_carrinho()

    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('loja.produtos'))

    # Busca produtos e calcula total
    itens = []
    total = 0

    for produto_id, item in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if produto and produto.ativo and produto.estoque >= item['quantidade']:
            subtotal = produto.preco * item['quantidade']
            total += subtotal
            itens.append({
                'produto': produto,
                'quantidade': item['quantidade'],
                'subtotal': subtotal
            })

    if not itens:
        flash('Nenhum produto disponível no carrinho.', 'warning')
        return redirect(url_for('loja.produtos'))

    # Busca endereços do usuário
    enderecos = Endereco.query.filter_by(usuario_id=current_user.id).all()

    return render_template('checkout/index.html', itens=itens, total=total, enderecos=enderecos)


@bp.route('/pagar', methods=['POST'])
@login_required
def pagar():
    """Inicia o processo de pagamento"""
    carrinho = _get_carrinho()

    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('loja.produtos'))

    # Busca produtos e valida estoque
    itens = []
    total = 0

    for produto_id, item in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if not produto or not produto.ativo:
            flash(f'O produto {produto.nome if produto else produto_id} não está mais disponível.', 'danger')
            return redirect(url_for('carrinho.index'))
        if produto.estoque < item['quantidade']:
            flash(f'Estoque insuficiente para {produto.nome}.', 'danger')
            return redirect(url_for('carrinho.index'))

        subtotal = produto.preco * item['quantidade']
        total += subtotal
        itens.append({
            'produto': produto,
            'quantidade': item['quantidade'],
            'subtotal': subtotal
        })

    # Obtém ou cria endereço
    endereco_id = request.form.get('endereco_id')
    if endereco_id:
        endereco = Endereco.query.get(int(endereco_id))
        if not endereco or endereco.usuario_id != current_user.id:
            flash('Endereço inválido.', 'danger')
            return redirect(url_for('checkout.index'))
    else:
        # Cria novo endereço
        cep = request.form.get('cep', '').strip()
        rua = request.form.get('rua', '').strip()
        numero = request.form.get('numero', '').strip()
        complemento = request.form.get('complemento', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()

        if not all([cep, rua, numero, bairro, cidade, estado]):
            flash('Preencha todos os campos obrigatórios do endereço.', 'danger')
            return redirect(url_for('checkout.index'))

        endereco = Endereco(
            usuario_id=current_user.id,
            cep=cep,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado
        )
        db.session.add(endereco)
        db.session.flush()  # Para obter o ID

    # Cria o pedido
    forma_pagamento = request.form.get('forma_pagamento')

    pedido = Pedido(
        usuario_id=current_user.id,
        endereco_id=endereco.id,
        total=total,
        forma_pagamento=forma_pagamento,
        status='pendente'
    )

    db.session.add(pedido)
    db.session.flush()  # Para obter o ID do pedido

    # Cria os itens do pedido
    for item in itens:
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_id=item['produto'].id,
            nome_produto=item['produto'].nome,
            preco=item['produto'].preco,
            quantidade=item['quantidade']
        )
        db.session.add(item_pedido)

        # Atualiza estoque
        item['produto'].estoque -= item['quantidade']

    db.session.commit()

    # Limpa carrinho
    _clear_carrinho()

    # Redireciona para o pagamento correto
    if forma_pagamento == 'pix':
        return redirect(url_for('checkout.pix', pedido_id=pedido.id))
    else:  # checkout_pro
        return redirect(url_for('checkout.checkout_pro', pedido_id=pedido.id))


@bp.route('/pix/<int:pedido_id>')
@login_required
def pix(pedido_id):
    """Redireciona para o PagBank Checkout com PIX"""
    pedido = Pedido.query.get_or_404(pedido_id)

    # Verifica se o pedido pertence ao usuário
    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    # Se ainda não tem código de pagamento, cria
    if not pedido.pg_payment_code or not pedido.pg_payment_link:
        try:
            from app.services.pagseguro import criar_pagamento_pix
            criar_pagamento_pix(pedido)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Erro ao criar pagamento PIX: {str(e)}')
            flash(f'Erro ao criar pagamento: {str(e)}', 'danger')
            return redirect(url_for('checkout.index'))

    # Redireciona para o checkout do PagBank (mesmo fluxo do cartão)
    if pedido.pg_payment_link:
        return redirect(pedido.pg_payment_link)
    else:
        flash('Link de pagamento não encontrado. Tente novamente.', 'warning')
        return redirect(url_for('checkout.detalhes_pedido', pedido_id=pedido_id))


@bp.route('/checkout-pro/<int:pedido_id>')
@login_required
def checkout_pro(pedido_id):
    """Redireciona para o PagBank Checkout"""
    pedido = Pedido.query.get_or_404(pedido_id)

    # Verifica se o pedido pertence ao usuário
    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    # Se ainda não tem código de pagamento, cria
    if not pedido.pg_payment_code or not pedido.pg_payment_link:
        try:
            from app.services.pagseguro import criar_checkout_pro
            itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
            checkout_url = criar_checkout_pro(pedido, itens)
            db.session.commit()
            return redirect(checkout_url)
        except Exception as e:
            flash(f'Erro ao criar pagamento: {str(e)}', 'danger')
            return redirect(url_for('checkout.index'))

    # Se já tem link de pagamento, redireciona para ele
    if pedido.pg_payment_link:
        return redirect(pedido.pg_payment_link)
    else:
        flash('Link de pagamento não encontrado. Tente novamente.', 'warning')
        return redirect(url_for('checkout.detalhes_pedido', pedido_id=pedido_id))


@bp.route('/sucesso/<int:pedido_id>')
@login_required
def sucesso(pedido_id):
    """Página de sucesso após pagamento"""
    pedido = Pedido.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    return render_template('checkout/sucesso.html', pedido=pedido)


@bp.route('/pendente/<int:pedido_id>')
@login_required
def pending(pedido_id):
    """Página de pagamento pendente"""
    pedido = Pedido.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    return render_template('checkout/pendente.html', pedido=pedido)


@bp.route('/falha/<int:pedido_id>')
@login_required
def falha(pedido_id):
    """Página de falha no pagamento"""
    pedido = Pedido.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    return render_template('checkout/falha.html', pedido=pedido)


@bp.route('/pedido/<int:pedido_id>')
@login_required
def detalhes_pedido(pedido_id):
    """Detalhes do pedido"""
    pedido = Pedido.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('loja.index'))

    return render_template('checkout/pedido.html', pedido=pedido)


@bp.route('/api/pedido/<int:pedido_id>/status')
@login_required
def api_pedido_status(pedido_id):
    """API para verificar status do pedido"""
    pedido = Pedido.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403

    return jsonify({
        'status': pedido.status,
        'mp_status': pedido.mp_payment_status
    })
