## Projeto: Confronto de Relatórios de RSC com Notícias

Este projeto faz duas coisas:

-   Coleta notícias em sites (a partir de uma lista de URLs) e filtra por menções a empresas e a termos socioambientais.
-   Analisa o tom (sentimento) dos textos (notícias e relatórios PDF) como positivo/negativo/neutro, e exporta relatórios em PDF.

### 1) Requisitos e instalação

Recomendado usar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Sem PyTorch os modelos Transformers ficam indisponíveis, mas há fallback léxico. Para melhor qualidade, instale PyTorch (CPU):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 2) Arquivos de entrada

Preencha os CSVs em `data/`:

-   `data/urls.csv`: coluna `url`.
-   `data/empresas.csv`: coluna `name` e opcional `regex`.
-   `data/termos.csv`: coluna `term` e opcional `regex`.

Coloque PDFs dos relatórios (se houver) em `data/relatorios/`.

### 3) Uso rápido (comando unificado)

-   Gerar PDF de notícias (scrape -> sentimento -> PDF) com defaults:

```bash
python -m csr_analyzer.cli pdf
```

-   Ajustes comuns (opcionais):

```bash
python -m csr_analyzer.cli pdf \
  --urls-file data/urls.csv \
  --empresas-file data/empresas.csv \
  --termos-file data/termos.csv \
  --output-pdf outputs/relatorio_noticias.pdf \
  --model lexicon \
  --limit 30
```

-   Se já existir um CSV com as notícias filtradas, pule o scraping:

```bash
python -m csr_analyzer.cli pdf --input-csv outputs/noticias_filtradas.csv
```

-   Gerar PDF de relatórios a partir dos PDFs em `data/relatorios/`:

```bash
python -m csr_analyzer.cli pdf --kind reports
```

-   Ajustes comuns (opcionais):

```bash
python -m csr_analyzer.cli pdf --kind reports \
  --reports-dir data/relatorios \
  --output-pdf outputs/relatorio_pdfs.pdf \
  --model lexicon \
  --limit 30
```

### 4) Comandos detalhados (avançado)

-   Coletar e filtrar notícias:

```bash
python -m csr_analyzer.cli scrape-news \
  --urls-file data/urls.csv \
  --empresas-file data/empresas.csv \
  --termos-file data/termos.csv \
  --output-file outputs/noticias_filtradas.csv
```

-   Analisar sentimento das notícias (entrada com coluna `text`):

```bash
python -m csr_analyzer.cli analyze-news \
  --input-file outputs/noticias_filtradas.csv \
  --output-file outputs/noticias_com_sentimento.csv \
  --model lexicon
```

-   Exportar PDF a partir de um CSV com resultados:

```bash
python -m csr_analyzer.cli export-pdf \
  --input-file outputs/noticias_com_sentimento.csv \
  --output-file outputs/relatorio_noticias.pdf \
  --kind news \
  --text-column text
```

-   Análise de relatórios PDF em lote e exportação:

```bash
python -m csr_analyzer.cli analyze-reports \
  --reports-dir data/relatorios \
  --output-file outputs/relatorios_com_sentimento.csv \
  --model lexicon

python -m csr_analyzer.cli export-pdf \
  --input-file outputs/relatorios_com_sentimento.csv \
  --output-file outputs/relatorio_pdfs.pdf \
  --kind reports \
  --text-column text_excerpt
```

### 5) Observações e ética

-   Respeite `robots.txt` e termos dos sites. Use `--request-delay` e limites.
-   O PDF agora possui um layout mais limpo, barra de título e cores por sentimento. Caracteres fora de Latin‑1 são normalizados.
-   Ajuste o modelo em `csr_analyzer/sentiment.py` se desejar outro.
