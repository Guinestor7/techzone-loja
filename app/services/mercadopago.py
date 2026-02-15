import os
import mercadopago
from flask import current_app, request


def get_sdk():
    """Retorna a instância do SDK do Mercado Pago"""
    access_token = current_app.config.get('MP_ACCESS_TOKEN')
    if not access_token:
        raise Exception('MP_ACCESS_TOKEN não configurado')
    return mercadopago.SDK(access_token)


def criar_pagamento_pix(pedido):
    """Cria um pagamento PIX no Mercado Pago"""
    sdk = get_sdk()

    # Formata CPF do usuário (remove caracteres não numéricos)
    cpf = pedido.usuario.cpf.replace('.', '').replace('-', '') if pedido.usuario.cpf else None

    payment_data = {
        "transaction_amount": float(pedido.total),
        "description": f"Pedido #{pedido.id}",
        "payment_method_id": "pix",
        "payer": {
            "email": pedido.usuario.email,
            "first_name": pedido.usuario.nome.split()[0] if pedido.usuario.nome else '',
            "last_name": ' '.join(pedido.usuario.nome.split()[1:]) if pedido.usuario.nome and len(pedido.usuario.nome.split()) > 1 else '',
            "identification": {
                "type": "CPF",
                "number": cpf or "00000000000"
            }
        },
        "external_reference": str(pedido.id)
    }

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response['response'] if 'response' in payment_response else payment_response

        # Salva dados do Pix no pedido
        pedido.mp_payment_id = str(payment.get('id', ''))
        pedido.mp_payment_status = payment.get('status', 'pending')

        # Obtém QR Code e código copia e cola
        if 'point_of_interaction' in payment:
            transaction_data = payment['point_of_interaction'].get('transaction_data', {})
            pedido.qr_code_pix = transaction_data.get('qr_code', '')
            pedido.pix_copy_paste = transaction_data.get('qr_code_base64', '')

        return payment
    except Exception as e:
        raise Exception(f'Erro ao criar pagamento Pix: {str(e)}')


def criar_preferencia_checkout_pro(pedido, itens):
    """Cria uma preferência para Checkout Pro (redirecionamento)"""
    sdk = get_sdk()

    # Monta lista de itens
    items_data = []
    for item in itens:
        items_data.append({
            "title": item.nome_produto,
            "quantity": item.quantidade,
            "unit_price": float(item.preco),
            "currency_id": "BRL"
        })

    # URLs de retorno
    from flask import url_for
    base_url = request.url_root.replace('http://', 'https://') if 'http://' in request.url_root else request.url_root

    preference_data = {
        "items": items_data,
        "external_reference": str(pedido.id),
        "back_urls": {
            "success": f"{base_url}checkout/sucesso/{pedido.id}",
            "failure": f"{base_url}checkout/falha/{pedido.id}",
            "pending": f"{base_url}checkout/pendente/{pedido.id}"
        },
        "auto_return": "approved",
        "binary_mode": False
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response['response'] if 'response' in preference_response else preference_response

        # Salva ID da preferência no pedido
        pedido.mp_preference_id = str(preference.get('id', ''))

        # Retorna URL de iniciação do checkout
        return preference.get('init_point', preference.get('sandbox_init_point', ''))
    except Exception as e:
        raise Exception(f'Erro ao criar preferência Checkout Pro: {str(e)}')


def consultar_pagamento(payment_id):
    """Consulta o status de um pagamento no Mercado Pago"""
    sdk = get_sdk()

    try:
        payment_response = sdk.payment().get(payment_id)
        payment = payment_response['response'] if 'response' in payment_response else payment_response
        return payment
    except Exception as e:
        raise Exception(f'Erro ao consultar pagamento: {str(e)}')


def webhook():
    """Webhook para receber notificações do Mercado Pago"""
    from app import db
    from app.models import Pedido

    data = request.get_json() or {}

    # Verifica se é uma notificação de pagamento
    if data.get('type') == 'payment':
        payment_id = data.get('data', {}).get('id')

        if payment_id:
            try:
                payment = consultar_pagamento(payment_id)
                external_reference = payment.get('external_reference')

                if external_reference:
                    pedido = Pedido.query.get(int(external_reference))

                    if pedido:
                        # Atualiza status do pedido
                        pedido.mp_payment_id = str(payment_id)
                        pedido.mp_payment_status = payment.get('status', 'unknown')

                        status_map = {
                            'approved': 'pago',
                            'pending': 'pendente',
                            'authorized': 'pago',
                            'in_process': 'pendente',
                            'rejected': 'cancelado',
                            'cancelled': 'cancelado',
                            'refunded': 'cancelado'
                        }

                        new_status = status_map.get(payment.get('status'), pedido.status)
                        pedido.status = new_status

                        db.session.commit()

            except Exception as e:
                current_app.logger.error(f'Erro no webhook: {str(e)}')
                return {'error': str(e)}, 500

    return {'status': 'ok'}, 200
