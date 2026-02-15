#!/bin/bash

# Script de Deploy para Produção
# Uso: ./deploy.sh [render|railway|vps]

set -e

ENV=${1:-vps}

echo "🚀 Iniciando deploy para: $ENV"

case $ENV in
  render)
    echo "📦 Deploy para Render..."
    # Instala Render CLI
    # npm install -g @render/cli

    # Login e deploy
    # render deploy
    echo "✅ Deploy para Render configurado!"
    echo "📌 Configure as variáveis de ambiente no painel do Render:"
    echo "   - SECRET_KEY"
    echo "   - PAGSEGURO_TOKEN"
    echo "   - PAGSEGURO_SANDBOX=False"
    ;;

  railway)
    echo "📦 Deploy para Railway..."
    # Instala Railway CLI
    # npm install -g @railway/cli

    # Login e deploy
    # railway login
    # railway init
    # railway up
    echo "✅ Deploy para Railway configurado!"
    ;;

  vps)
    echo "📦 Deploy para VPS com Docker..."
    echo "📋 Passos:"
    echo "   1. Suba os arquivos para o servidor"
    echo "   2. Execute: docker-compose up -d"
    echo "   3. Execute: flask db upgrade"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "   docker-compose logs -f      # Ver logs"
    echo "   docker-compose restart       # Reiniciar"
    echo "   docker-compose down          # Parar"
    ;;

  *)
    echo "❌ Ambiente não reconhecido: $ENV"
    echo "Use: ./deploy.sh [render|railway|vps]"
    exit 1
    ;;
esac

echo ""
echo "⚠️  Não esqueça de configurar:"
echo "   - Token PagBank de PRODUÇÃO"
echo "   - SECRET_KEY seguro"
echo "   - Banco de dados PostgreSQL"
echo "   - URL do webhook no PagBank: https://seu-site.com/webhook/pagbank"
