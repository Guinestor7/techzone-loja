# 🚀 Deploy em Produção - TechZone

## 📋 Pré-requisitos

Antes de fazer o deploy, você precisa:

1. **Token PagBank de Produção**
   - Acesse: https://developer.pagbank.com.br
   - Crie uma conta ou faça login
   - Gere um token de produção (não sandbox!)

2. **SECRET_KEY seguro**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Banco de Dados**
   - PostgreSQL (Render/Railway/VPS)

## 🎯 Opções de Deploy

### Opção 1: Render (Mais Fácil)

1. **Crie uma conta em** https://render.com

2. **Fork este repositório** no GitHub

3. **No Render, crie:**
   - **New PostgreSQL Database** → nome: `techzone-db`
   - **New Web Service** → conecte seu repositório GitHub

4. **Configure o Web Service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app --bind 0.0.0.0:5000 --workers 4`
   - Environment Variables:
     ```
     FLASK_ENV=production
     PYTHONUNBUFFERED=true
     DATABASE_URL=(conexão do banco criado)
     SECRET_KEY=(chave gerada)
     PAGSEGURO_TOKEN=(seu token produção)
     PAGSEGURO_SANDBOX=False
     ```

5. **Execute migrations:**
   - No Render Shell: `flask db upgrade`

6. **Configure o Webhook PagBank:**
   - URL: `https://seu-app.onrender.com/webhook/pagbank`

---

### Opção 2: Railway

1. **Instale a CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login e deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Configure as variáveis no painel Railway**

---

### Opção 3: VPS Próprio com Docker

1. **No servidor, instale Docker:**
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```

2. **Copie os arquivos:**
   ```bash
   git clone seu-repositorio
   cd teste-site-meu
   ```

3. **Configure o .env:**
   ```bash
   cp .env.production.example .env
   nano .env  # edite as variáveis
   ```

4. **Inicie:**
   ```bash
   docker-compose up -d
   ```

5. **Execute migrations:**
   ```bash
   docker-compose exec app flask db upgrade
   ```

---

## 🔧 Variáveis de Ambiente Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta Flask | `abc123...` (32+ caracteres hex) |
| `DATABASE_URL` | Conexão PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `PAGSEGURO_TOKEN` | Token PagBank produção | `Bearer XXX...` |
| `PAGSEGURO_SANDBOX` | Modo sandbox | `False` |

---

## 📊 Pós-Deploy

### 1. Configure o Webhook PagBank

No painel do PagBank, adicione a URL:
```
https://seu-dominio.com/webhook/pagbank
```

### 2. Teste o Pagamento

1. Crie um pedido de teste
2. Redirecione para o PagBank
3. Faça um pagamento PIX de teste
4. Verifique se o webhook atualiza o status

### 3. Monitore os Logs

```bash
# Render/Railway: painel visual
# Docker:
docker-compose logs -f app
```

---

## 🔒 Segurança

- ✅ HTTPS habilitado (obrigatório para PagBank)
- ✅ Variáveis de ambiente configuradas
- ✅ `.env` no `.gitignore`
- ✅ PostgreSQL ao invés de SQLite
- ✅ Gunicorn (não dev server)

---

## 💡 Troubleshooting

**Erro 401 no PagBank:**
- Verifique se o token é de PRODUÇÃO
- Confirme `PAGSEGURO_SANDBOX=False`

**Webhook não funciona:**
- URL deve ser HTTPS
- Verifique se a rota `/webhook/pagbank` está acessível
- Logs do PagBank mostram tentativas

**Erro 500:**
- Verifique logs da aplicação
- Execute `flask db upgrade`
- Confirme variáveis de ambiente
