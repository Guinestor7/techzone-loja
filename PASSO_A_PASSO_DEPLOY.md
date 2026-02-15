# 🚀 PASSO A PASSO - DEPLOY NO RENDER

Siga exatamente这些 passos para colocar seu site no ar!

---

## PASSO 1: Criar conta no GitHub

1. Acesse: https://github.com
2. Faça login ou crie uma conta (grátis)
3. Crie um **NOVO REPOSITÓRIO**:
   - Nome: `techzone-loja` (ou outro que preferir)
   - Deixe **Público** ou **Privado** (como preferir)
   - **NÃO** marque nenhuma opção de inicializar

---

## PASSO 2: Enviar código para o GitHub

No seu terminal, execute:

```bash
cd /home/sea/git/teste-site-meu

# Adicione o remoto (SUBSTITUA SEU_USUÁRIO)
git remote add origin https://github.com/SEU_USUARIO/techzone-loja.git

# Renomeia branch para main
git branch -M main

# Envia o código
git push -u origin main
```

---

## PASSO 3: Criar conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started"**
3. Faça login com **GitHub** (mais fácil)
4. Autorize o Render a acessar seu repositório

---

## PASSO 4: Criar Banco de Dados PostgreSQL

1. No painel do Render, clique em **"+"** (New)
2. Selecione **"PostgreSQL"**
3. Configure:
   - **Name**: `techzone-db`
   - **Database**: `techzone`
   - **User**: `techzone`
   - **Region**: São Paulo (ou mais próxima)
   - **Plan**: **Free** (ou pago se preferir)
4. Clique em **"Create Database"**

⏳ **AGUARDE** o banco ser criado (uns 2-3 minutos)

5. Quando terminar, **COPIE** a **Internal Database URL** (vai precisar dela!)

---

## PASSO 5: Criar o Web Service

1. No Render, clique em **"+"** novamente
2. Selecione **"Web Service"**
3. Clique em **"Connect GitHub"** (se não conectou)
4. Selecione o repositório `techzone-loja`
5. Clique em **"Connect"**

6. Configure o Web Service:

   | Campo | Valor |
   |-------|-------|
   | **Name** | `techzone-api` |
   | **Region** | São Paulo |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn run:app --bind 0.0.0.0:5000 --workers 4` |

7. **Clique em "Advanced"** para configurar variáveis de ambiente:

   Clique em **"Add Environment Variable"** e adicione:

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `PYTHONUNBUFFERED` | `true` |
   | `SECRET_KEY` | `gere_uma_chave_abaixo` |
   | `DATABASE_URL` | `cole_a_url_do_banco_aqui` |
   | `PAGSEGURO_TOKEN` | `seu_token_pagbank` |
   | `PAGSEGURO_SANDBOX` | `False` |

8. **GERAR SECRET_KEY** (cole no campo SECRET_KEY acima):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

9. **COPIAR DATABASE URL**:
   - Volte na página do banco (Passo 4)
   - Copie a **Internal Database URL**
   - Cole no campo `DATABASE_URL`

10. **COPIAR TOKEN PAGBANK**:
    - Acesse: https://developer.pagbank.com.br
    - Faça login
    - Vá em "Gerencie suas chaves"
    - Copie o **Token de Produção** (não sandbox!)

11. Clique em **"Create Web Service"**

⏳ **AGUARDE** o deploy (demora uns 5-10 minutos na primeira vez)

---

## PASSO 6: Executar Migrations (Criar tabelas)

1. Quando o deploy terminar, clique no seu Web Service
2. No menu lateral, clique em **"Shell"**
3. No terminal que abrir, digite:
   ```bash
   flask db upgrade
   ```
4. Crie um usuário admin:
   ```bash
   python
   ```
   ```python
   from app import create_app, db
   from app.models import User

   app = create_app()
   with app.app_context():
       admin = User(email='admin@techzone.com', nome='Admin', is_admin=True)
       admin.set_senha('sua_senha_aqui')
       db.session.add(admin)
       db.session.commit()
       print("Admin criado!")
   ```
   ```python
   exit()
   ```

---

## PASSO 7: Testar!

1. No Render, clique no link do seu site (ex: `https://techzone-api.onrender.com`)
2. Teste:
   - ✅ A página carrega?
   - ✅ Consegue fazer login?
   - ✅ Criar um produto?

---

## PASSO 8: Configurar Webhook PagBank

1. Acesse: https://developer.pagbank.com.br
2. Vá em **"Webhooks"** ou **"Preferências de notificação"**
3. Adicione a URL:
   ```
   https://SEU_SITE.onrender.com/webhook/pagbank
   ```
4. Salve

---

## ✅ PRONTO!

Seu site está no ar! URL será algo como:
```
https://techzone-api.onrender.com
```

---

## ❌ PROBLEMAS?

**Erro no deploy:**
- Clique em **"Logs"** no Render para ver o erro
- Me mande o erro que te ajudo!

**Webhook não funciona:**
- O site precisa estar no ar (https) para webhook funcionar
- Verifique se a URL está correta

**Pagamento falha:**
- Verifique se `PAGSEGURO_SANDBOX=False`
- Confirme se o token é de PRODUÇÃO
