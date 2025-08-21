#!/bin/bash
# Script simples para gerar relatório

echo "=== Gerador de Relatório de Notícias ==="
echo ""

# Verificar se ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🔧 Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Verificar se os arquivos de dados existem
if [ ! -f "data/urls.csv" ]; then
    echo "❌ Arquivo data/urls.csv não encontrado!"
    echo "   Configure os arquivos em data/ primeiro."
    exit 1
fi

if [ ! -f "data/empresas.csv" ]; then
    echo "❌ Arquivo data/empresas.csv não encontrado!"
    echo "   Configure os arquivos em data/ primeiro."
    exit 1
fi

if [ ! -f "data/termos.csv" ]; then
    echo "❌ Arquivo data/termos.csv não encontrado!"
    echo "   Configure os arquivos em data/ primeiro."
    exit 1
fi

echo "📰 Coletando e analisando notícias..."
echo "   (Isso pode demorar alguns minutos)"
echo ""

# Executar o comando
python -m csr_analyzer.cli run

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Relatório gerado com sucesso!"
    echo "📄 Arquivo: outputs/relatorio_noticias.pdf"
else
    echo ""
    echo "❌ Erro ao gerar relatório"
    exit 1
fi

