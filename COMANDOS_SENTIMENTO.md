# Comandos para Análise de Sentimento

Este documento lista todos os comandos disponíveis para gerar/substituir relatórios de sentimento dos documentos em `relatorios_empresas`.

## 🚀 Comandos Disponíveis

### 1. Script Python Simples (Recomendado)

```bash
python gerar_relatorio_sentimento.py
```

**O que faz:**

-   Processa todos os PDFs em `relatorios_empresas/`
-   Gera/substitui relatórios CSV para cada arquivo
-   Cria pastas individuais para cada PDF
-   Mostra resumo completo da análise

### 2. Script Shell (Linux/Mac)

```bash
./gerar_relatorio_sentimento.sh
```

**O que faz:**

-   Mesma funcionalidade do script Python
-   Verifica se Python está instalado
-   Interface amigável no terminal

### 3. Script Batch (Windows)

```cmd
gerar_relatorio_sentimento.bat
```

**O que faz:**

-   Mesma funcionalidade do script Python
-   Verifica se Python está instalado
-   Pausa no final para visualizar resultados

### 4. Via CLI do Sistema

```bash
# Comando simples
python -m csr_analyzer.cli analyze-sentiment

# Comando com parâmetros personalizados
python -m csr_analyzer.cli analyze-pdf-sentiment \
    --reports-dir relatorios_empresas \
    --positive-words data/palavras_positivas.csv \
    --negative-words data/palavras_negativas.csv \
    --output-dir outputs
```

## 📁 Estrutura de Saída

Após executar qualquer comando, será criada a seguinte estrutura:

```
outputs/
├── Relatório Anual 2023 - BB/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
├── Relatório ESG 2023 - Petrobras/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
└── ...
```

## 🔄 Substituição Automática

-   **Todos os comandos substituem automaticamente** os relatórios existentes
-   Não é necessário deletar pastas antigas
-   Os CSVs são sempre atualizados com os dados mais recentes

## 📊 Exemplo de Saída

```
🚀 GERANDO RELATÓRIO DE SENTIMENTO
==================================================
🔧 Inicializando analisador...
📁 Processando arquivos em: relatorios_empresas
Encontrados 3 arquivos para processar
Processando: relatorios_empresas/Relatório Anual 2023 - BB.pdf
✓ Processado: Relatório Anual 2023 - BB.pdf - Positivo: 0.0235, Negativo: 0.0088, Total palavras: 1918
Processando: relatorios_empresas/Relatório ESG 2023 - Petrobras.pdf
✓ Processado: Relatório ESG 2023 - Petrobras.pdf - Positivo: 0.0189, Negativo: 0.0123, Total palavras: 2156
Processando: relatorios_empresas/Relatório Sustentabilidade 2023 - Vale.pdf
✓ Processado: Relatório Sustentabilidade 2023 - Vale.pdf - Positivo: 0.0212, Negativo: 0.0098, Total palavras: 1834

💾 Salvando relatórios...
✓ Relatórios salvos para Relatório Anual 2023 - BB.pdf:
  - Positivo: outputs/Relatório Anual 2023 - BB/resultado_positivo.csv
  - Negativo: outputs/Relatório Anual 2023 - BB/resultado_negativo.csv
✓ Relatórios salvos para Relatório ESG 2023 - Petrobras.pdf:
  - Positivo: outputs/Relatório ESG 2023 - Petrobras/resultado_positivo.csv
  - Negativo: outputs/Relatório ESG 2023 - Petrobras/resultado_negativo.csv
✓ Relatórios salvos para Relatório Sustentabilidade 2023 - Vale.pdf:
  - Positivo: outputs/Relatório Sustentabilidade 2023 - Vale/resultado_positivo.csv
  - Negativo: outputs/Relatório Sustentabilidade 2023 - Vale/resultado_negativo.csv

📊 === RESUMO FINAL ===
✅ Total de arquivos processados: 3
📈 Média de palavras positivas: 0.021200
📉 Média de palavras negativas: 0.010300
📝 Total de palavras processadas: 5908
😊 Total de palavras positivas: 125
😞 Total de palavras negativas: 61

🎉 RELATÓRIO GERADO COM SUCESSO!
📂 Relatórios CSV salvos em 3 pastas:
   1. Relatório Anual 2023 - BB/
      ├── resultado_positivo.csv
      └── resultado_negativo.csv
   2. Relatório ESG 2023 - Petrobras/
      ├── resultado_positivo.csv
      └── resultado_negativo.csv
   3. Relatório Sustentabilidade 2023 - Vale/
      ├── resultado_positivo.csv
      └── resultado_negativo.csv

💡 Dica: Os arquivos foram salvos/substituídos em outputs/
   Cada PDF tem sua própria pasta com os resultados em CSV.
```

## ⚡ Comando Mais Rápido

Para uso diário, recomendo o comando mais simples:

```bash
python gerar_relatorio_sentimento.py
```

Este comando:

-   ✅ É o mais rápido
-   ✅ Não precisa de parâmetros
-   ✅ Usa configurações padrão
-   ✅ Substitui automaticamente relatórios antigos
-   ✅ Mostra resumo completo
