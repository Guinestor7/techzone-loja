"""
Serviço para gerar QR Code PIX estático usando APIs gratuitas
Como alternativa quando não há token de API disponível
"""
import qrcode
import io
import base64
from flask import current_app


def criar_qr_code_pix(pedido):
    """
    Gera um QR Code PIX estático com os dados do pagamento
    Usando qrcode library para gerar a imagem
    """
    from app.models import ItemPedido

    # Obtém a chave PIX configurada
    pix_key = current_app.config.get('PIX_CHAVE', '')
    pix_banco = current_app.config.get('PIX_NOME_BANCO', '')
    pix_tipo = current_app.config.get('PIX_TIPO_CHAVE', 'email')

    if not pix_key:
        raise Exception('Chave PIX não configurada. Configure PIX_CHAVE no .env')

    # Busca os itens do pedido
    itens_pedido = ItemPedido.query.filter_by(pedido_id=pedido.id).all()

    # Monta a descrição dos itens
    descricao_itens = ", ".join([f"{item.quantidade}x {item.nome_produto}" for item in itens_pedido])

    # Cria o payload do PIX (formato BR Code)
    # Este é um formato simplificado - para produção use uma API de PIX real
    payload_pix = f"""
================================
DADOS PARA PAGAMENTO PIX
================================
Chave: {pix_key}
Tipo: {pix_tipo}
Banco: {pix_banco}
Valor: R$ {pedido.total:.2f}
Referência: Pedido #{pedido.id}
Itens: {descricao_itens}
================================
    """.strip()

    # Gera o QR Code com os dados
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_pix)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Converte para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Salva no pedido
    pedido.qr_code_pix = img_str
    pedido.pix_copy_paste = pix_key

    return {'code': str(pedido.id), 'link': pix_key}


def criar_link_pagamento_cartao(pedido):
    """
    Cria um link de pagamento para cartão
    Como alternativa, retorna um link para página de pagamento manual
    """
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    return f'{base_url}/checkout/pagar-cartao/{pedido.id}'
