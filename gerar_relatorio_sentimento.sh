#!/bin/bash

# Script para gerar relatório de sentimento de todos os PDFs
# em relatorios_empresas

echo "🚀 Iniciando análise de sentimento..."
echo "======================================"

# Verifica se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro."
    exit 1
fi

# Executa o script Python
python3 gerar_relatorio_sentimento.py

echo ""
echo "✅ Processo concluído!"
echo "📁 Verifique os resultados na pasta outputs/"
