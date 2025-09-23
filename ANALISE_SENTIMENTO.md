# Análise de Sentimento de PDFs

Este módulo implementa análise de sentimento baseada em léxico para arquivos PDF, utilizando listas de palavras positivas e negativas em português.

## Funcionalidades

-   **Tokenização**: Quebra o texto em palavras individuais
-   **Remoção de stop words**: Remove palavras comuns que não contribuem para o sentimento
-   **Análise baseada em léxico**: Usa listas de palavras positivas e negativas
-   **Processamento de PDFs**: Extrai texto de arquivos PDF automaticamente
-   **Relatórios detalhados**: Gera relatórios separados para resultados positivos e negativos

## Como Usar

### 1. Via CLI (Recomendado)

```bash
# Análise básica com configurações padrão
python -m csr_analyzer.cli analyze-pdf-sentiment

# Análise com configurações personalizadas
python -m csr_analyzer.cli analyze-pdf-sentiment \
    --reports-dir relatorios_empresas \
    --positive-words data/palavras_positivas.csv \
    --negative-words data/palavras_negativas.csv \
    --output-dir outputs \
    --report-name Meu_Relatorio
```

### 2. Via Script Python

```python
from csr_analyzer.pdf_sentiment_processor import PDFSentimentProcessor

# Inicializa o processador
processor = PDFSentimentProcessor(
    positive_words_path="data/palavras_positivas.csv",
    negative_words_path="data/palavras_negativas.csv"
)

# Processa todos os PDFs
results = processor.process_all_pdfs("relatorios_empresas")

# Salva os resultados
positive_file, negative_file = processor.save_results(
    results,
    output_dir="outputs",
    report_name="Relatorio_Sentimento"
)
```

### 3. Via Script de Exemplo

```bash
python exemplo_analise_sentimento.py
```

## Estrutura de Arquivos

```
relatorios_empresas/          # Pasta com os PDFs para análise
├── Relatório Anual 2023 - BB.pdf
├── relatorio_empresa2.pdf
└── ...

data/                         # Arquivos de palavras
├── palavras_positivas.csv    # Lista de palavras positivas
└── palavras_negativas.csv    # Lista de palavras negativas

outputs/                      # Resultados da análise
├── Relatório Anual 2023 - BB/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
├── relatorio_empresa2/
│   ├── resultado_positivo.csv
│   └── resultado_negativo.csv
└── ...
```

## Método de Cálculo

### Resultado Positivo

```
Proporção Positiva = Número de palavras positivas / Total de palavras
```

### Resultado Negativo

```
Proporção Negativa = Número de palavras negativas / Total de palavras
```

### Processo de Análise

1. **Extração de texto**: O texto é extraído dos PDFs
2. **Tokenização**: O texto é dividido em palavras individuais
3. **Limpeza**: Remove pontuação e converte para minúsculas
4. **Filtragem**: Remove stop words e palavras muito curtas
5. **Contagem**: Conta palavras positivas e negativas
6. **Cálculo**: Calcula as proporções em relação ao total de palavras

## Exemplo de Saída

### Arquivo `resultado_positivo.csv`

```csv
Arquivo,Proporção_Positiva,Contagem_Positiva,Total_Palavras
Relatório Anual 2023 - BB.pdf,0.023456,45,1918
```

### Arquivo `resultado_negativo.csv`

```csv
Arquivo,Proporção_Negativa,Contagem_Negativa,Total_Palavras
Relatório Anual 2023 - BB.pdf,0.008765,17,1918
```

### Estrutura de Pastas

Para cada arquivo PDF processado, é criada uma pasta com o nome do arquivo (sem extensão):

-   `outputs/Relatório Anual 2023 - BB/` (para o arquivo `Relatório Anual 2023 - BB.pdf`)
-   `outputs/relatorio_empresa2/` (para o arquivo `relatorio_empresa2.pdf`)

## Configurações

### Parâmetros do CLI

-   `--reports-dir`: Diretório com os arquivos PDF (padrão: `relatorios_empresas`)
-   `--positive-words`: Arquivo CSV com palavras positivas (padrão: `data/palavras_positivas.csv`)
-   `--negative-words`: Arquivo CSV com palavras negativas (padrão: `data/palavras_negativas.csv`)
-   `--output-dir`: Diretório de saída (padrão: `outputs`)

### Stop Words

O sistema remove automaticamente palavras comuns em português como:

-   Artigos: a, o, as, os, um, uma
-   Preposições: de, da, do, em, para, por
-   Conjunções: e, ou, mas, que
-   Pronomes: eu, tu, ele, ela, nós, vocês
-   E outras palavras que não contribuem para o sentimento

## Requisitos

-   Python 3.7+
-   pypdf (para extração de texto de PDFs)
-   Arquivos CSV com palavras positivas e negativas

## Limitações

-   A análise é baseada apenas em palavras individuais (não considera contexto)
-   Não detecta ironia ou sarcasmo
-   Depende da qualidade das listas de palavras positivas/negativas
-   Não considera a intensidade das palavras (todas têm peso igual)
