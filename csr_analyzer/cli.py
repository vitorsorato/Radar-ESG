import argparse
import os
from typing import List, Optional

import pandas as pd

from .scraper import scrape_news
from .sentiment import SentimentAnalyzer
from .pdf_utils import extract_text_from_pdf
from .report_pdf import AnalysisPDF
from .pdf_sentiment_processor import PDFSentimentProcessor


def _ensure_dir_exists(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def cmd_scrape_news(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_file)
    result_df = scrape_news(
        urls_file=args.urls_file,
        companies_file=args.empresas_file,
        terms_file=args.termos_file,
        max_articles_per_site=args.max_articles_per_site,
        request_delay=args.request_delay,
        homepage_link_limit=args.homepage_link_limit,
        feed_item_limit=args.feed_item_limit,
    )
    result_df.to_csv(args.output_file, index=False)
    print(f"Salvo: {args.output_file} ({len(result_df)} notícias)")


def _apply_sentiment_to_dataframe(df: pd.DataFrame, text_column: str, analyzer: SentimentAnalyzer) -> pd.DataFrame:
    texts: List[str] = df[text_column].fillna("").astype(str).tolist()
    outputs = analyzer.analyze_batch(texts)
    labels = [o["label"] for o in outputs]
    scores = [o["score"] for o in outputs]
    df = df.copy()
    df["sentiment_label"] = labels
    df["sentiment_score"] = scores
    return df


def cmd_analyze_news(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_file)
    df = pd.read_csv(args.input_file)
    model_name = args.model
    analyzer = SentimentAnalyzer(model_name=model_name) if model_name else SentimentAnalyzer()
    df_out = _apply_sentiment_to_dataframe(df, text_column=args.text_column, analyzer=analyzer)
    df_out.to_csv(args.output_file, index=False)
    print(f"Salvo: {args.output_file} ({len(df_out)} linhas)")


def cmd_analyze_reports(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_file)
    model_name = args.model
    analyzer = SentimentAnalyzer(model_name=model_name) if model_name else SentimentAnalyzer()

    rows = []
    pdf_dir = args.reports_dir
    chunk_size = args.chunk_size
    for root, _dirs, files in os.walk(pdf_dir):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue
            fpath = os.path.join(root, fname)
            text = extract_text_from_pdf(fpath, max_pages=args.max_pages)
            if not text:
                continue
            # Chunking
            chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] if chunk_size else [text]
            sentiments = analyzer.analyze_batch(chunks)
            for idx, (chunk, sent) in enumerate(zip(chunks, sentiments)):
                rows.append(
                    {
                        "file": fpath,
                        "chunk_index": idx,
                        "text_excerpt": chunk[:300],
                        "sentiment_label": sent["label"],
                        "sentiment_score": sent["score"],
                    }
                )

    df = pd.DataFrame(rows)
    df.to_csv(args.output_file, index=False)
    print(f"Salvo: {args.output_file} ({len(df)} linhas)")


def cmd_export_pdf(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_file)
    df = pd.read_csv(args.input_file)
    title = args.title or ("Análise de Notícias" if args.kind == "news" else "Análise de Relatórios")
    pdf = AnalysisPDF(title=title)
    pdf.add_summary(df, kind=("Notícias" if args.kind == "news" else "Relatórios"))

    if args.kind == "news":
        pdf.add_items(
            df,
            title_col="title" if "title" in df.columns else args.text_column,
            text_col=args.text_column,
            meta_cols=[c for c in ["url", "site", "published", "matched_companies", "matched_terms", "sentiment_label", "sentiment_score"] if c in df.columns],
            limit=args.limit,
        )
    else:
        pdf.add_items(
            df,
            title_col="file" if "file" in df.columns else args.text_column,
            text_col=args.text_column if args.text_column in df.columns else ("text_excerpt" if "text_excerpt" in df.columns else "text"),
            meta_cols=[c for c in ["chunk_index", "sentiment_label", "sentiment_score"] if c in df.columns],
            limit=args.limit,
        )

    pdf.output(args.output_file)
    print(f"PDF gerado em: {args.output_file}")


def cmd_news_pdf(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_pdf)
    # Step 1: Get news DataFrame (from CSV if provided, otherwise scrape)
    if args.input_csv and os.path.exists(args.input_csv):
        news_df = pd.read_csv(args.input_csv)
    else:
        news_df = scrape_news(
            urls_file=args.urls_file,
            companies_file=args.empresas_file,
            terms_file=args.termos_file,
            max_articles_per_site=args.max_articles_per_site,
            request_delay=args.request_delay,
            homepage_link_limit=args.homepage_link_limit,
            feed_item_limit=args.feed_item_limit,
        )
        if args.output_csv:
            _ensure_dir_exists(args.output_csv)
            news_df.to_csv(args.output_csv, index=False)
    # Step 2: Sentiment
    analyzer = SentimentAnalyzer(model_name=args.model) if args.model else SentimentAnalyzer()
    news_df = _apply_sentiment_to_dataframe(news_df, text_column=args.text_column, analyzer=analyzer)
    if args.output_sentiment_csv:
        _ensure_dir_exists(args.output_sentiment_csv)
        news_df.to_csv(args.output_sentiment_csv, index=False)
    # Step 3: PDF
    pdf = AnalysisPDF(title=args.title or "Análise de Notícias")
    pdf.add_summary(news_df, kind="Notícias")
    pdf.add_items(
        news_df,
        title_col="title" if "title" in news_df.columns else args.text_column,
        text_col=args.text_column,
        meta_cols=[c for c in ["url", "site", "published", "matched_companies", "matched_terms", "sentiment_label", "sentiment_score"] if c in news_df.columns],
        limit=args.limit,
    )
    pdf.output(args.output_pdf)
    print(f"PDF gerado em: {args.output_pdf}")


def cmd_reports_pdf(args: argparse.Namespace) -> None:
    _ensure_dir_exists(args.output_pdf)
    # Step 1: Analyze PDFs
    analyzer = SentimentAnalyzer(model_name=args.model) if args.model else SentimentAnalyzer()
    rows = []
    chunk_size = args.chunk_size
    for root, _dirs, files in os.walk(args.reports_dir):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue
            fpath = os.path.join(root, fname)
            text = extract_text_from_pdf(fpath, max_pages=args.max_pages)
            if not text:
                continue
            chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] if chunk_size else [text]
            sentiments = analyzer.analyze_batch(chunks)
            for idx, (chunk, sent) in enumerate(zip(chunks, sentiments)):
                rows.append(
                    {
                        "file": fpath,
                        "chunk_index": idx,
                        "text_excerpt": chunk[:300],
                        "sentiment_label": sent["label"],
                        "sentiment_score": sent["score"],
                    }
                )
    df = pd.DataFrame(rows)
    if args.output_sentiment_csv:
        _ensure_dir_exists(args.output_sentiment_csv)
        df.to_csv(args.output_sentiment_csv, index=False)
    # Step 2: PDF
    pdf = AnalysisPDF(title=args.title or "Análise de Relatórios")
    pdf.add_summary(df, kind="Relatórios")
    pdf.add_items(
        df,
        title_col="file" if "file" in df.columns else args.text_column,
        text_col=args.text_column if args.text_column in df.columns else ("text_excerpt" if "text_excerpt" in df.columns else "text"),
        meta_cols=[c for c in ["chunk_index", "sentiment_label", "sentiment_score"] if c in df.columns],
        limit=args.limit,
    )
    pdf.output(args.output_pdf)
    print(f"PDF gerado em: {args.output_pdf}")


def cmd_analyze_pdf_sentiment(args: argparse.Namespace) -> None:
    """Analisa sentimento de PDFs usando léxico de palavras positivas/negativas."""
    processor = PDFSentimentProcessor(
        positive_words_path=args.positive_words,
        negative_words_path=args.negative_words
    )
    
    # Processa todos os PDFs
    results = processor.process_all_pdfs(args.reports_dir)
    
    if not results:
        print("Nenhum PDF foi processado com sucesso.")
        return
    
    # Salva os resultados
    saved_files = processor.save_results(
        results, 
        output_dir=args.output_dir
    )
    
    # Exibe resumo
    summary = processor.generate_report_summary(results)
    print(f"\n=== RESUMO DA ANÁLISE ===")
    print(f"Total de arquivos processados: {summary['total_files']}")
    print(f"Média de palavras positivas: {summary['avg_positive']:.6f}")
    print(f"Média de palavras negativas: {summary['avg_negative']:.6f}")
    print(f"Total de palavras processadas: {summary['total_words_processed']}")
    print(f"Total de palavras positivas encontradas: {summary['total_positive_count']}")
    print(f"Total de palavras negativas encontradas: {summary['total_negative_count']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI - Scraping e Análise de Sentimento")
    sub = parser.add_subparsers(dest="command", required=True)

    # scrape-news
    p_scrape = sub.add_parser("scrape-news", help="Coleta notícias e filtra por empresas/termos")
    p_scrape.add_argument("--urls-file", required=True, help="CSV com coluna 'url'")
    p_scrape.add_argument("--empresas-file", required=True, help="CSV com coluna 'name' e opcional 'regex'")
    p_scrape.add_argument("--termos-file", required=True, help="CSV com coluna 'term' e opcional 'regex'")
    p_scrape.add_argument("--output-file", required=True, help="CSV de saída com notícias filtradas")
    p_scrape.add_argument("--max-articles-per-site", type=int, default=100)
    p_scrape.add_argument("--request-delay", type=float, default=0.2, help="Delay entre requisições (seg)")
    p_scrape.add_argument("--homepage-link-limit", type=int, default=100)
    p_scrape.add_argument("--feed-item-limit", type=int, default=200)
    p_scrape.set_defaults(func=cmd_scrape_news)

    # analyze-news
    p_news = sub.add_parser("analyze-news", help="Analisa sentimento de notícias (CSV)")
    p_news.add_argument("--input-file", required=True, help="CSV com coluna de texto")
    p_news.add_argument("--output-file", required=True, help="CSV de saída com sentimento")
    p_news.add_argument("--text-column", default="text")
    p_news.add_argument("--model", default=None, help="Nome do modelo Transformers ou 'lexicon'")
    p_news.set_defaults(func=cmd_analyze_news)

    # analyze-reports
    p_rep = sub.add_parser("analyze-reports", help="Analisa sentimento de relatórios PDF em um diretório")
    p_rep.add_argument("--reports-dir", required=True, help="Diretório com arquivos PDF")
    p_rep.add_argument("--output-file", required=True, help="CSV de saída")
    p_rep.add_argument("--chunk-size", type=int, default=8000, help="Tamanho dos blocos de texto (caracteres)")
    p_rep.add_argument("--max-pages", type=int, default=None, help="Limitar número de páginas lidas por PDF")
    p_rep.add_argument("--model", default=None, help="Nome do modelo Transformers ou 'lexicon'")
    p_rep.set_defaults(func=cmd_analyze_reports)

    # export-pdf
    p_pdf = sub.add_parser("export-pdf", help="Exporta um CSV de análise para PDF")
    p_pdf.add_argument("--input-file", required=True, help="CSV de entrada com resultados")
    p_pdf.add_argument("--output-file", required=True, help="Arquivo PDF de saída")
    p_pdf.add_argument("--kind", choices=["news", "reports"], default="news")
    p_pdf.add_argument("--text-column", default="text", help="Nome da coluna de texto principal")
    p_pdf.add_argument("--title", default=None, help="Título do PDF")
    p_pdf.add_argument("--limit", type=int, default=20, help="Máximo de itens no PDF")
    p_pdf.set_defaults(func=cmd_export_pdf)

    # news-pdf (simplified one-shot)
    p_npdf = sub.add_parser("news-pdf", help="Executa pipeline completo de notícias e gera PDF")
    p_npdf.add_argument("--urls-file", default="data/urls.csv")
    p_npdf.add_argument("--empresas-file", default="data/empresas.csv")
    p_npdf.add_argument("--termos-file", default="data/termos.csv")
    p_npdf.add_argument("--input-csv", default=None, help="Se fornecido, usa CSV existente em vez de fazer scraping")
    p_npdf.add_argument("--output-pdf", default="outputs/relatorio_noticias.pdf")
    p_npdf.add_argument("--output-csv", default=None, help="Opcional: salvar CSV filtrado")
    p_npdf.add_argument("--output-sentiment-csv", default=None, help="Opcional: salvar CSV com sentimento")
    p_npdf.add_argument("--text-column", default="text")
    p_npdf.add_argument("--model", default="lexicon")
    p_npdf.add_argument("--max-articles-per-site", type=int, default=50)
    p_npdf.add_argument("--request-delay", type=float, default=0.2)
    p_npdf.add_argument("--homepage-link-limit", type=int, default=80)
    p_npdf.add_argument("--feed-item-limit", type=int, default=160)
    p_npdf.add_argument("--limit", type=int, default=30)
    p_npdf.add_argument("--title", default=None)
    p_npdf.set_defaults(func=cmd_news_pdf)

    # reports-pdf (simplified one-shot)
    p_rpdf = sub.add_parser("reports-pdf", help="Executa pipeline de relatórios PDF e gera PDF")
    p_rpdf.add_argument("--reports-dir", default="data/relatorios")
    p_rpdf.add_argument("--output-pdf", default="outputs/relatorio_pdfs.pdf")
    p_rpdf.add_argument("--output-sentiment-csv", default=None)
    p_rpdf.add_argument("--chunk-size", type=int, default=8000)
    p_rpdf.add_argument("--max-pages", type=int, default=None)
    p_rpdf.add_argument("--model", default="lexicon")
    p_rpdf.add_argument("--text-column", default="text_excerpt")
    p_rpdf.add_argument("--limit", type=int, default=30)
    p_rpdf.add_argument("--title", default=None)
    p_rpdf.set_defaults(func=cmd_reports_pdf)

    # unified pdf command (even simpler)
    p_updf = sub.add_parser("pdf", help="Gera PDF a partir de notícias (default) ou relatórios")
    p_updf.add_argument("--kind", choices=["news", "reports"], default="news", help="Tipo de relatório")
    # news options (ignored if kind=reports)
    p_updf.add_argument("--urls-file", default="data/urls.csv")
    p_updf.add_argument("--empresas-file", default="data/empresas.csv")
    p_updf.add_argument("--termos-file", default="data/termos.csv")
    p_updf.add_argument("--input-csv", default=None, help="Se fornecido, usa CSV existente em vez de fazer scraping")
    # reports options (ignored if kind=news)
    p_updf.add_argument("--reports-dir", default="data/relatorios", help="Diretório com PDFs")
    p_updf.add_argument("--chunk-size", type=int, default=8000)
    p_updf.add_argument("--max-pages", type=int, default=None)
    # shared
    p_updf.add_argument("--output-pdf", default="outputs/relatorio_noticias.pdf")
    p_updf.add_argument("--output-sentiment-csv", default=None)
    p_updf.add_argument("--text-column", default="text")
    p_updf.add_argument("--model", default="lexicon")
    p_updf.add_argument("--limit", type=int, default=30)
    p_updf.add_argument("--title", default=None)

    def _cmd_unified_pdf(a: argparse.Namespace) -> None:
        # Adjust default output name when switching kinds
        if a.kind == "reports" and (not a.output_pdf or a.output_pdf == "outputs/relatorio_noticias.pdf"):
            a.output_pdf = "outputs/relatorio_pdfs.pdf"

        if a.kind == "news":
            # Reuse news-pdf implementation
            cmd_news_pdf(a)
        else:
            # Reuse reports-pdf implementation
            # Ensure default text column aligns with reports
            if not hasattr(a, "text_column") or a.text_column is None:
                a.text_column = "text_excerpt"
            cmd_reports_pdf(a)

    p_updf.set_defaults(func=_cmd_unified_pdf)

    # analyze-pdf-sentiment (lexicon-based sentiment analysis)
    p_sentiment = sub.add_parser("analyze-pdf-sentiment", help="Analisa sentimento de PDFs usando léxico de palavras positivas/negativas")
    p_sentiment.add_argument("--reports-dir", default="relatorios_empresas", help="Diretório com arquivos PDF")
    p_sentiment.add_argument("--positive-words", default="data/palavras_positivas.csv", help="Arquivo CSV com palavras positivas")
    p_sentiment.add_argument("--negative-words", default="data/palavras_negativas.csv", help="Arquivo CSV com palavras negativas")
    p_sentiment.add_argument("--output-dir", default="outputs", help="Diretório de saída")
    p_sentiment.set_defaults(func=cmd_analyze_pdf_sentiment)

    # run (super simple command)
    p_run = sub.add_parser("run", help="Comando simples: gera relatório de notícias")
    p_run.set_defaults(func=lambda args: cmd_news_pdf(argparse.Namespace(
        urls_file="data/urls.csv",
        empresas_file="data/empresas.csv",
        termos_file="data/termos.csv",
        input_csv=None,
        output_pdf="outputs/relatorio_noticias.pdf",
        output_csv=None,
        output_sentiment_csv=None,
        text_column="text",
        model="lexicon",
        max_articles_per_site=50,
        request_delay=0.2,
        homepage_link_limit=80,
        feed_item_limit=160,
        limit=30,
        title=None
    )))

    # analyze-sentiment (comando simples para análise de sentimento)
    p_sentiment_simple = sub.add_parser("analyze-sentiment", help="Comando simples: analisa sentimento de todos os PDFs em relatorios_empresas")
    p_sentiment_simple.set_defaults(func=lambda args: cmd_analyze_pdf_sentiment(argparse.Namespace(
        reports_dir="relatorios_empresas",
        positive_words="data/palavras_positivas.csv",
        negative_words="data/palavras_negativas.csv",
        output_dir="outputs"
    )))

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
