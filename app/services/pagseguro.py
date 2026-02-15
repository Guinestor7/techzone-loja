"""
Integração com PagBank Checkout API
Documentação: https://developer.pagbank.com.br/reference/criar-checkout
"""
import requests
import json
from flask import current_app, request
from datetime import datetime, timedelta


def get_credentials():
    """Retorna as credenciais do PagBank"""
    token = current_app.config.get('PAGSEGURO_TOKEN')
    sandbox = current_app.config.get('PAGSEGURO_SANDBOX', False)

    if not token:
        raise Exception('Token do PagBank não configurado')

    return {
        'token': token,
        'sandbox': sandbox
    }


def get_base_url():
    """Retorna a URL base do PagBank"""
    creds = get_credentials()
    if creds['sandbox']:
        return 'https://sandbox.api.pagseguro.com'
    return 'https://api.pagseguro.com'


def get_headers():
    """Retorna os headers para requisições à API do PagBank"""
    creds = get_credentials()
    token = creds['token']
    # Formato: Bearer <token>
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


def criar_checkout(pedido, itens):
    """
    Cria um checkout PagBank usando a nova API de Checkouts
    Endpoint: POST /checkouts
    Documentação: https://developer.pagbank.com.br/reference/criar-checkout

    Retorna o link de pagamento para redirecionar o cliente
    """
    base_url = get_base_url()
    headers = get_headers()

    # Dados do pedido
    user = pedido.cliente
    endereco = pedido.endereco_entrega

    # URL de retorno - usa URL fixa menor para evitar erro
    base_url_request = request.url_root if request else 'http://localhost:5000/'
    # Remove barras duplicadas e garante formato correto
    base_url_request = base_url_request.rstrip('/')

    # Monta os itens no formato da API
    items_data = []
    for item in itens:
        items_data.append({
            'name': item.nome_produto[:100],
            'quantity': item.quantidade,
            'unit_amount': int(float(item.preco) * 100)  # Valor em centavos
        })

    # Monta os dados do cliente
    customer_data = {
        'name': user.nome[:50] if user.nome else 'Cliente',
        'email': user.email,
        'tax_id': (user.cpf or '').replace('.', '').replace('-', '') if hasattr(user, 'cpf') and user.cpf else None
    }

    # Remove tax_id se for None
    if not customer_data['tax_id']:
        del customer_data['tax_id']

    # Monta os dados de endereço/shipping se disponível
    shipping_data = None
    if endereco and endereco.rua:
        shipping_data = {
            'type': 'FIXED',  # Valores válidos: FIXED, FREE, CALCULATED
            'amount': 0,  # Valor do frete em centavos (0 = frete grátis)
            'service_type': 'SEDEX',  # Valores válidos: SEDEX, PAC
            'address': {
                'street': endereco.rua or '',
                'number': endereco.numero or '1',
                'complement': endereco.complemento or '',
                'locality': endereco.bairro or '',
                'city': endereco.cidade or '',
                'region_code': endereco.estado or '',
                'country': 'BRA',
                'postal_code': endereco.cep.replace('-', '') if endereco.cep else ''
            },
            'address_modifiable': False  # Cliente não pode alterar o endereço
        }

    # Data de expiração do checkout (2 horas a partir de agora)
    expiration_date = (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S-03:00')

    # Monta o payload principal
    payload = {
        'reference_id': str(pedido.id),
        'customer': customer_data,
        'items': items_data,
        'expiration_date': expiration_date,
        'payment_methods': [
            {'type': 'CREDIT_CARD'},
            {'type': 'DEBIT_CARD'},
            {'type': 'PIX'}
        ]
    }

    # URLs - PagBank não aceita localhost em sandbox
    # Só envia as URLs se não for localhost/127.0.0.1
    if not any(x in base_url_request for x in ['localhost', '127.0.0.1']):
        redirect_url = f'{base_url_request}/checkout/sucesso/{pedido.id}'
        if len(redirect_url) <= 255:  # Limite da API
            payload['redirect_url'] = redirect_url

        notification_url = f'{base_url_request}/webhook/pagbank'
        if len(notification_url) <= 100:  # Limite da API
            payload['notification_urls'] = [notification_url]

    # Adiciona shipping se disponível
    if shipping_data:
        payload['shipping'] = shipping_data

    try:
        current_app.logger.info(f'PagBank Checkout Request: {json.dumps(payload, indent=2)}')

        response = requests.post(
            f'{base_url}/checkouts',
            headers=headers,
            json=payload,
            timeout=30
        )

        current_app.logger.info(f'PagBank Checkout Response Status: {response.status_code}')
        current_app.logger.info(f'PagBank Checkout Response: {response.text[:1000] if response.text else "No response"}')

        if response.status_code in [200, 201, 202]:
            data = response.json()

            # Salva o código do checkout
            pedido.pg_payment_code = data.get('id', '')

            # Busca o link de pagamento (link com rel="PAY")
            checkout_links = data.get('links', [])
            checkout_url = None

            for link in checkout_links:
                if link.get('rel') == 'PAY':
                    checkout_url = link.get('href')
                    break

            # Se não encontrou PAY, busca SELF
            if not checkout_url:
                for link in checkout_links:
                    if link.get('rel') == 'SELF':
                        checkout_url = link.get('href')
                        break

            if checkout_url:
                pedido.pg_payment_link = checkout_url
                return checkout_url
            else:
                # Última tentativa: pega o primeiro link disponível
                if checkout_links:
                    pedido.pg_payment_link = checkout_links[0].get('href', '')
                    return checkout_links[0].get('href', '')
                else:
                    raise Exception('Não foi encontrado link de checkout na resposta')

        elif response.status_code == 401:
            raise Exception('Token de autenticação inválido. Verifique se o token está correto.')
        else:
            error_msg = response.text if response.text else f'HTTP {response.status_code}'
            raise Exception(f'Erro ao criar checkout: {error_msg}')

    except Exception as e:
        current_app.logger.error(f'Erro PagBank Checkout: {str(e)}')
        raise Exception(f'Erro na integração PagBank: {str(e)}')


def criar_pagamento_pix(pedido):
    """
    Cria um checkout PagBank com PIX como método principal
    Usa a mesma API de checkout mas com apenas PIX como opção
    """
    from app.models import ItemPedido

    base_url = get_base_url()
    headers = get_headers()

    # Dados do pedido
    user = pedido.cliente
    endereco = pedido.endereco_entrega

    # URL de retorno - usa URL fixa menor para evitar erro
    base_url_request = request.url_root if request else 'http://localhost:5000/'
    base_url_request = base_url_request.rstrip('/')

    # Monta os itens do carrinho
    itens_pedido = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
    items_data = []
    for item in itens_pedido:
        items_data.append({
            'name': item.nome_produto[:100],
            'quantity': item.quantidade,
            'unit_amount': int(float(item.preco) * 100)  # Valor em centavos
        })

    # Monta os dados do cliente
    customer_data = {
        'name': user.nome[:50] if user.nome else 'Cliente',
        'email': user.email,
        'tax_id': (user.cpf or '').replace('.', '').replace('-', '') if hasattr(user, 'cpf') and user.cpf else None
    }

    # Remove tax_id se for None
    if not customer_data['tax_id']:
        del customer_data['tax_id']

    # Monta os dados de endereço/shipping se disponível
    shipping_data = None
    if endereco and endereco.rua:
        shipping_data = {
            'type': 'FIXED',  # Valores válidos: FIXED, FREE, CALCULATED
            'amount': 0,  # Valor do frete em centavos (0 = frete grátis)
            'service_type': 'SEDEX',  # Valores válidos: SEDEX, PAC
            'address': {
                'street': endereco.rua or '',
                'number': endereco.numero or '1',
                'complement': endereco.complemento or '',
                'locality': endereco.bairro or '',
                'city': endereco.cidade or '',
                'region_code': endereco.estado or '',
                'country': 'BRA',
                'postal_code': endereco.cep.replace('-', '') if endereco.cep else ''
            },
            'address_modifiable': False  # Cliente não pode alterar o endereço
        }

    # Data de expiração do checkout (2 horas a partir de agora)
    expiration_date = (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S-03:00')

    # Monta o payload com apenas PIX como opção de pagamento
    payload = {
        'reference_id': str(pedido.id),
        'customer': customer_data,
        'items': items_data,
        'expiration_date': expiration_date,
        'payment_methods': [
            {'type': 'PIX'}
        ]
    }

    # URLs - PagBank não aceita localhost em sandbox
    # Só envia as URLs se não for localhost/127.0.0.1
    if not any(x in base_url_request for x in ['localhost', '127.0.0.1']):
        redirect_url = f'{base_url_request}/checkout/sucesso/{pedido.id}'
        if len(redirect_url) <= 255:  # Limite da API
            payload['redirect_url'] = redirect_url

        notification_url = f'{base_url_request}/webhook/pagbank'
        if len(notification_url) <= 100:  # Limite da API
            payload['notification_urls'] = [notification_url]

    # Adiciona shipping se disponível
    if shipping_data:
        payload['shipping'] = shipping_data

    try:
        current_app.logger.info(f'PagBank PIX Request: {json.dumps(payload, indent=2)}')

        response = requests.post(
            f'{base_url}/checkouts',
            headers=headers,
            json=payload,
            timeout=30
        )

        current_app.logger.info(f'PagBank PIX Response Status: {response.status_code}')
        current_app.logger.info(f'PagBank PIX Response: {response.text[:1000] if response.text else "No response"}')

        if response.status_code in [200, 201, 202]:
            data = response.json()

            # Salva o código do checkout
            pedido.pg_payment_code = data.get('id', '')

            # Busca o link de pagamento (link com rel="PAY")
            checkout_links = data.get('links', [])
            checkout_url = None

            for link in checkout_links:
                if link.get('rel') == 'PAY':
                    checkout_url = link.get('href')
                    break

            # Se não encontrou PAY, busca SELF
            if not checkout_url:
                for link in checkout_links:
                    if link.get('rel') == 'SELF':
                        checkout_url = link.get('href')
                        break

            if checkout_url:
                pedido.pg_payment_link = checkout_url
                return {'code': pedido.pg_payment_code, 'link': checkout_url}
            else:
                if checkout_links:
                    checkout_url = checkout_links[0].get('href', '')
                    pedido.pg_payment_link = checkout_url
                    return {'code': pedido.pg_payment_code, 'link': checkout_url}
                else:
                    raise Exception('Não foi encontrado link de checkout na resposta')

        elif response.status_code == 401:
            raise Exception('Token de autenticação inválido. Verifique se o token está correto.')
        else:
            error_msg = response.text if response.text else f'HTTP {response.status_code}'
            raise Exception(f'Erro ao criar pagamento PIX: {error_msg}')

    except Exception as e:
        current_app.logger.error(f'Erro PagBank PIX: {str(e)}')
        raise Exception(f'Erro na integração PagBank: {str(e)}')


def criar_checkout_pro(pedido, itens):
    """
    Cria um checkout PagBank para pagamento com cartão
    Usa a nova API de Checkouts
    """
    return criar_checkout(pedido, itens)


def consultar_checkout(checkout_id):
    """
    Consulta o status de um checkout no PagBank
    """
    base_url = get_base_url()
    headers = get_headers()

    try:
        response = requests.get(
            f'{base_url}/checkouts/{checkout_id}',
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()

            # Mapeamento de status do checkout
            status = data.get('status', '').lower()
            status_map = {
                'created': 'pendente',
                'paid': 'pago',
                'canceled': 'cancelado',
                'payment_failed': 'cancelado',
                'waiting_payment': 'pendente',
                'expired': 'cancelado'
            }

            return {
                'status': status_map.get(status, 'pendente'),
                'status_raw': status,
                'code': checkout_id
            }
        else:
            raise Exception(f'Erro ao consultar checkout: {response.content}')

    except Exception as e:
        raise Exception(f'Erro ao consultar checkout PagBank: {str(e)}')


def webhook_notificacao(notification_data):
    """
    Processa notificações do PagBank (webhook)
    """
    try:
        reference_id = notification_data.get('reference_id')
        status = notification_data.get('status', '').lower()

        status_map = {
            'created': 'pendente',
            'paid': 'pago',
            'canceled': 'cancelado',
            'payment_failed': 'cancelado'
        }

        return {
            'reference': reference_id,
            'status': status_map.get(status, 'pendente'),
            'status_raw': status
        }

    except Exception as e:
        current_app.logger.error(f'Erro no webhook PagBank: {str(e)}')
        return None


# Funções legadas para compatibilidade
def criar_session_pagseguro(pedido, itens):
    """Não usado na nova API"""
    return None

def consultar_transacao(code):
    """Alias para consultar_checkout"""
    return consultar_checkout(code)
