# 🔑 Criar Token de Acesso ao GitHub

O GitHub não aceita mais senha. Você precisa criar um Token.

## Passo 1: Criar o Token

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Configure:
   - **Note**: `TechZone Deploy`
   - **Expiration**: `90 days` (ou o que preferir)
   - **Scopes**: marque **repo** (isso dá acesso aos seus repositórios)
4. Clique em **"Generate token"**

## Passo 2: Copiar o Token

⚠️ **COPIE O TOKEN AGORA!** Ele aparece assim:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

(Você não verá esse token novamente!)

## Passo 3: Usar o Token

No terminal, quando pedir senha:

```
Username: Guinestor7
Password: [COLE O TOKEN AQUI]
```

**O token não aparece na tela** (é normal, por segurança)

---

## SOLUÇÃO ALTERNATIVA: Usar SSH (Mais fácil para sempre)

Se não quiser ficar usando token toda vez:

```bash
# 1. Gere uma chave SSH
ssh-keygen -t ed25519 -C "seu-email@gmail.com"
# Aperte Enter em tudo (não precisa de senha)

# 2. Mostre a chave pública
cat ~/.ssh/id_ed25519.pub
```

Copie o resultado e adicione em:
https://github.com/settings/keys → **New SSH key**

Depois use:
```bash
git remote set-url origin git@github.com:Guinestor7/techzone-loja.git
git push -u origin main
```

Assim não pede senha nunca mais!
