import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações base da aplicação"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-padrao-desenvolvimento-123456')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///loja.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    # Upload de imagens
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # PagSeguro
    PAGSEGURO_EMAIL = os.getenv('PAGSEGURO_EMAIL')
    PAGSEGURO_TOKEN = os.getenv('PAGSEGURO_TOKEN')
    PAGSEGURO_SANDBOX = os.getenv('PAGSEGURO_SANDBOX', 'True').lower() == 'true'

    # Pix Direto (sem intermediário)
    PIX_CHAVE = os.getenv('PIX_CHAVE', '')
    PIX_NOME_BANCO = os.getenv('PIX_NOME_BANCO', '')
    PIX_TIPO_CHAVE = os.getenv('PIX_TIPO_CHAVE', 'email')

    # Mercado Pago (mantido para compatibilidade)
    MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')
    MP_WEBHOOK_SECRET = os.getenv('MP_WEBHOOK_SECRET')


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
