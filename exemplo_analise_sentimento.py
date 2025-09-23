#!/usr/bin/env python3
"""
Exemplo de uso do analisador de sentimento de PDFs.
Este script demonstra como usar a funcionalidade de análise de sentimento
baseada em léxico para processar PDFs na pasta relatorios_empresas.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from csr_analyzer.pdf_sentiment_processor import PDFSentimentProcessor


def main():
    """Função principal que executa a análise de sentimento."""
    print("=== ANÁLISADOR DE SENTIMENTO DE PDFs ===\n")
    
    # Verifica se os arquivos de palavras existem
    positive_words_path = "data/palavras_positivas.csv"
    negative_words_path = "data/palavras_negativas.csv"
    
    if not os.path.exists(positive_words_path):
        print(f"❌ Arquivo não encontrado: {positive_words_path}")
        return
    
    if not os.path.exists(negative_words_path):
        print(f"❌ Arquivo não encontrado: {negative_words_path}")
        return
    
    # Verifica se a pasta de relatórios existe
    reports_dir = "relatorios_empresas"
    if not os.path.exists(reports_dir):
        print(f"❌ Pasta não encontrada: {reports_dir}")
        print("   Crie a pasta e adicione alguns arquivos PDF para análise.")
        return
    
    # Inicializa o processador
    print("🔧 Inicializando analisador de sentimento...")
    processor = PDFSentimentProcessor(
        positive_words_path=positive_words_path,
        negative_words_path=negative_words_path
    )
    
    # Processa todos os PDFs
    print(f"📁 Processando PDFs em: {reports_dir}")
    results = processor.process_all_pdfs(reports_dir)
    
    if not results:
        print("❌ Nenhum PDF foi processado com sucesso.")
        print("   Verifique se há arquivos PDF na pasta relatorios_empresas.")
        return
    
    # Salva os resultados
    print("\n💾 Salvando relatórios...")
    saved_files = processor.save_results(
        results, 
        output_dir="outputs"
    )
    
    # Exibe resumo
    summary = processor.generate_report_summary(results)
    print(f"\n📊 === RESUMO DA ANÁLISE ===")
    print(f"Total de arquivos processados: {summary['total_files']}")
    print(f"Média de palavras positivas: {summary['avg_positive']:.6f}")
    print(f"Média de palavras negativas: {summary['avg_negative']:.6f}")
    print(f"Total de palavras processadas: {summary['total_words_processed']}")
    print(f"Total de palavras positivas encontradas: {summary['total_positive_count']}")
    print(f"Total de palavras negativas encontradas: {summary['total_negative_count']}")
    
    print(f"\n✅ Análise concluída!")
    print(f"📄 Relatórios CSV salvos em {len(saved_files)} pastas:")
    for i, (pos_file, neg_file) in enumerate(saved_files, 1):
        print(f"   {i}. {Path(pos_file).parent.name}/")
        print(f"      - resultado_positivo.csv")
        print(f"      - resultado_negativo.csv")


if __name__ == "__main__":
    main()
