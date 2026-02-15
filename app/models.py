from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='cliente', lazy='dynamic')
    enderecos = db.relationship('Endereco', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')

    def set_senha(self, senha):
        """Define a senha hash do usuário"""
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<User {self.email}>'


class Endereco(db.Model):
    """Modelo de endereço"""
    __tablename__ = 'enderecos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cep = db.Column(db.String(9))
    rua = db.Column(db.String(100))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))
    bairro = db.Column(db.String(50))
    cidade = db.Column(db.String(50))
    estado = db.Column(db.String(2))

    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='endereco_entrega', lazy='dynamic')

    def __repr__(self):
        return f'<Endereco {self.rua}, {self.numero} - {self.cidade}/{self.estado}>'


class Categoria(db.Model):
    """Modelo de categoria de produtos"""
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    produtos = db.relationship('Produto', backref='categoria', lazy='dynamic')

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Produto(db.Model):
    """Modelo de produto"""
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    preco_antigo = db.Column(db.Float)  # Para mostrar desconto
    estoque = db.Column(db.Integer, default=0)
    imagem = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy='dynamic')

    @property
    def desconto_percentual(self):
        """Calcula o percentual de desconto"""
        if self.preco_antigo and self.preco_antigo > self.preco:
            return int(((self.preco_antigo - self.preco) / self.preco_antigo) * 100)
        return 0

    def __repr__(self):
        return f'<Produto {self.nome} - R${self.preco}>'


class Pedido(db.Model):
    """Modelo de pedido"""
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente', nullable=False)  # pendente, pago, enviando, entregue, cancelado
    total = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(50))  # pix, checkout_pro

    # Mercado Pago
    mp_payment_id = db.Column(db.String(100))  # ID do pagamento no Mercado Pago
    mp_preference_id = db.Column(db.String(100))  # ID da preferência (Checkout Pro)
    mp_payment_status = db.Column(db.String(50))  # Status no Mercado Pago

    # PagSeguro
    pg_payment_code = db.Column(db.String(100))  # ID da transação PagSeguro
    pg_payment_link = db.Column(db.String(500))  # Link de pagamento PagSeguro

    # Pix (genérico)
    qr_code_pix = db.Column(db.Text)  # QR Code para Pix
    pix_copy_paste = db.Column(db.String(500))  # Código Pix copia e cola

    endereco_id = db.Column(db.Integer, db.ForeignKey('enderecos.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    itens = db.relationship('ItemPedido', backref='pedido', lazy='dynamic',
                           cascade='all, delete-orphan')

    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        status_map = {
            'pendente': 'Pendente',
            'pago': 'Pago',
            'enviando': 'Enviando',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        }
        return status_map.get(self.status, self.status)

    def __repr__(self):
        return f'<Pedido #{self.id} - {self.status} - R${self.total}>'


class ItemPedido(db.Model):
    """Modelo de item do pedido"""
    __tablename__ = 'itens_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    nome_produto = db.Column(db.String(100))  # Salva o nome na hora da compra
    preco = db.Column(db.Float, nullable=False)  # Salva o preço na hora da compra
    quantidade = db.Column(db.Integer, default=1)

    @property
    def subtotal(self):
        """Calcula o subtotal do item"""
        return self.preco * self.quantidade

    def __repr__(self):
        return f'<ItemPedido {self.nome_produto} x{self.quantidade}>'
