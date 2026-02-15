# 📦 Criar Repositório no GitHub

## Passo 1: Acessar GitHub

1. Acesse: https://github.com/new
2. Faça login se necessário

## Passo 2: Criar o Repositório

Preencha assim:

| Campo | Valor |
|-------|-------|
| **Repository name** | `techzone-loja` |
| **Description** | E-commerce TechZone |
| **Public/Private** | Private (ou Public como preferir) |

⚠️ **IMPORTANTE**: **NÃO** marque estas caixas:
- ❌ Add a README file
- ❌ Add .gitignore
- ❌ Choose a license

3. Clique em **"Create repository"**

## Passo 3: Voltar ao terminal

Depois de criar, execute:

```bash
git push -u origin main
```

---

## 🔑 Se pedir senha/token:

1. Crie seu token em: https://github.com/settings/tokens/new
   - Note: `TechZone`
   - Expiration: `90 days`
   - Marque **repo**
   - Generate token

2. Use o token como senha quando pedir
