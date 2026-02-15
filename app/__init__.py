from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db  # Importa db de models

# Inicializa extensões
migrate = None  # Será inicializado no create_app
login_manager = LoginManager()


def create_app(config_name='development'):
    """Factory pattern para criar a app Flask"""
    import os
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])

    # Inicializa extensões com a app
    from flask_migrate import Migrate
    global migrate
    migrate = Migrate()

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader para Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Criar pasta de upload se não existir
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Registrar blueprints
    from app.routes import loja, carrinho, checkout, auth, webhook
    app.register_blueprint(loja.bp)
    app.register_blueprint(carrinho.bp, url_prefix='/carrinho')
    app.register_blueprint(checkout.bp, url_prefix='/checkout')
    app.register_blueprint(auth.bp, url_prefix='/conta')
    app.register_blueprint(webhook.bp, url_prefix='/webhook')

    from app.admin import produtos, pedidos
    app.register_blueprint(produtos.bp, url_prefix='/admin')
    app.register_blueprint(pedidos.bp, url_prefix='/admin')

    # Registrar webhook do Mercado Pago (legado)
    from app.services.mercadopago import webhook
    app.route('/webhook/mercadopago', methods=['POST'])(webhook)

    return app
