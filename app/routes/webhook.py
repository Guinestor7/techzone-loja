"""
Rotas de webhook para processamento de pagamentos
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Pedido
import hmac
import hashlib

bp = Blueprint('webhook', __name__)


@bp.route('/pagbank', methods=['POST'])
def pagbank():
    """
    Webhook para receber notificações do PagBank
    """
    from app.services.pagseguro import consultar_transacao

    try:
        data = request.get_json()

        # PagBank envia notificações com o formato:
        # {
        #   "reference_id": "pedido_id",
        #   "charges": [...],
        #   "status": "PAID"
        # }

        # Tenta obter o reference_id (id do pedido)
        reference_id = data.get('reference_id')

        if not reference_id:
            # Tenta obter do formato de notificação
            charges = data.get('charges', [])
            if charges and len(charges) > 0:
                reference_id = charges[0].get('reference_id')

        if reference_id:
            pedido = Pedido.query.get(int(reference_id))

            if pedido:
                # Verifica o status do pagamento
                status = data.get('status', '').lower()

                if status == 'paid':
                    pedido.status = 'pago'
                    pedido.mp_payment_status = 'approved'
                elif status in ['canceled', 'payment_failed']:
                    pedido.status = 'cancelado'
                    pedido.mp_payment_status = status
                elif status == 'created':
                    pedido.status = 'pendente'
                    pedido.mp_payment_status = 'pending'

                db.session.commit()

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f'Erro no webhook PagBank: {str(e)}')
        return jsonify({'error': str(e)}), 500


@bp.route('/pagseguro', methods=['POST'])
def pagseguro():
    """
    Webhook legado para PagSeguro (mantido para compatibilidade)
    """
    notification_code = request.form.get('notificationCode')
    notification_type = request.form.get('notificationType')

    if notification_code:
        from app.services.pagseguro import webhook_notificacao
        result = webhook_notificacao(notification_code, notification_type)

        if result:
            pedido = Pedido.query.get(int(result['reference']))
            if pedido:
                status_map = {
                    '1': 'pendente',
                    '2': 'em_processamento',
                    '3': 'pago',
                    '4': 'pago',
                    '5': 'disputa',
                    '6': 'devolvido',
                    '7': 'cancelado'
                }
                pedido.status = status_map.get(result['status'], 'pendente')
                db.session.commit()

    return '', 200
