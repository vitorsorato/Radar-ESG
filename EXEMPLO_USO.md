# Exemplo de Uso - Análise de Sentimento de PDFs

Este documento mostra como usar o sistema de análise de sentimento implementado.

## Estrutura de Entrada

```
relatorios_empresas/
├── Relatório Anual 2023 - BB.pdf
├── Relatório ESG 2023 - Petrobras.pdf
└── Relatório Sustentabilidade 2023 - Vale.pdf
```

## Como Executar

### Método 1: Script de Exemplo (Recomendado)

```bash
python exemplo_analise_sentimento.py
```

### Método 2: Via CLI

```bash
python -m csr_analyzer.cli analyze-pdf-sentiment
```

### Método 3: Com Parâmetros Personalizados

```bash
python -m csr_analyzer.cli analyze-pdf-sentiment \
    --reports-dir relatorios_empresas \
    --positive-words data/palavras_positivas.csv \
    --negative-words data/palavras_negativas.csv \
    --output-dir outputs
```

## Estrutura de Saída

Após a execução, será criada a seguinte estrutura:

```
outputs/
├── Relatório Anual 2023 - BB/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
├── Relatório ESG 2023 - Petrobras/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
└── Relatório Sustentabilidade 2023 - Vale/
    ├── resultado_positivo.csv
    └── resultado_negativo.csv
```

## Exemplo de Conteúdo dos CSVs

### resultado_positivo.csv

```csv
Arquivo,Proporção_Positiva,Contagem_Positiva,Total_Palavras
Relatório Anual 2023 - BB.pdf,0.023456,45,1918
```

### resultado_negativo.csv

```csv
Arquivo,Proporção_Negativa,Contagem_Negativa,Total_Palavras
Relatório Anual 2023 - BB.pdf,0.008765,17,1918
```

## Interpretação dos Resultados

-   **Proporção_Positiva**: Número de palavras positivas dividido pelo total de palavras
-   **Proporção_Negativa**: Número de palavras negativas dividido pelo total de palavras
-   **Contagem_Positiva**: Número absoluto de palavras positivas encontradas
-   **Contagem_Negativa**: Número absoluto de palavras negativas encontradas
-   **Total_Palavras**: Total de palavras processadas (após remoção de stop words)

## Exemplo de Saída no Terminal

```
=== ANÁLISADOR DE SENTIMENTO DE PDFs ===

🔧 Inicializando analisador de sentimento...
📁 Processando PDFs em: relatorios_empresas
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

📊 === RESUMO DA ANÁLISE ===
Total de arquivos processados: 3
Média de palavras positivas: 0.021200
Média de palavras negativas: 0.010300
Total de palavras processadas: 5908
Total de palavras positivas encontradas: 125
Total de palavras negativas encontradas: 61

✅ Análise concluída!
📄 Relatórios CSV salvos em 3 pastas:
   1. Relatório Anual 2023 - BB/
      - resultado_positivo.csv
      - resultado_negativo.csv
   2. Relatório ESG 2023 - Petrobras/
      - resultado_positivo.csv
      - resultado_negativo.csv
   3. Relatório Sustentabilidade 2023 - Vale/
      - resultado_positivo.csv
      - resultado_negativo.csv
```

## Notas Importantes

1. **Nomes de Arquivos**: O sistema usa o nome do arquivo (sem extensão) para criar a pasta de saída
2. **Formato CSV**: Todos os resultados são salvos em formato CSV para facilitar análise posterior
3. **Processamento**: Cada arquivo é processado individualmente e gera sua própria pasta
4. **Encoding**: Todos os arquivos são salvos com encoding UTF-8
5. **Substituição**: Se a pasta já existir, os arquivos serão substituídos
