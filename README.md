# TechZone - E-commerce de Acessórios para Celular

E-commerce desenvolvido com Flask para venda de produtos eletrônicos e acessórios para celular.

## Tecnologias

- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Migrações**: Flask-Migrate
- **Autenticação**: Flask-Login
- **Pagamento**: Mercado Pago (Pix + Checkout Pro)
- **Frontend**: Bootstrap 5 + Jinja2

## Instalação

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais do Mercado Pago
```

4. Inicialize o banco de dados:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Crie dados iniciais:
```bash
flask init-data
```

6. Execute o servidor:
```bash
python run.py
```

O site estará disponível em http://localhost:5000

## Acesso Admin

Após executar `flask init-data`:
- Email: `admin@loja.com`
- Senha: `admin123`

**IMPORTANTE**: Altere essas credenciais em produção!

## Estrutura do Projeto

```
app/
├── __init__.py         # Factory da aplicação
├── config.py           # Configurações
├── models.py           # Modelos do banco de dados
├── routes/             # Rotas públicas
├── admin/              # Rotas admin
└── services/           # Integrações externas
```

## Mercado Pago

1. Crie uma conta em [mercadopago.com.br](https://www.mercadopago.com.br/developers)
2. Crie um Access Token em suas credenciais
3. Configure o webhook para: `https://seu-dominio.com/webhook/mercadopago`
4. Adicione as credenciais no arquivo `.env`

## Licença

MIT
