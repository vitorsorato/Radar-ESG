#!/usr/bin/env python3
"""
Script simples para gerar/substituir relatório de sentimento de todos os documentos
na pasta relatorios_empresas.
"""

import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from csr_analyzer.pdf_sentiment_processor import PDFSentimentProcessor


def main():
    """Gera/substitui relatório de sentimento de todos os documentos."""
    print("🚀 GERANDO RELATÓRIO DE SENTIMENTO")
    print("=" * 50)
    
    # Verifica se os arquivos necessários existem
    positive_words_path = "data/palavras_positivas.csv"
    negative_words_path = "data/palavras_negativas.csv"
    reports_dir = "relatorios_empresas"
    
    if not Path(positive_words_path).exists():
        print(f"❌ Erro: Arquivo não encontrado: {positive_words_path}")
        return
    
    if not Path(negative_words_path).exists():
        print(f"❌ Erro: Arquivo não encontrado: {negative_words_path}")
        return
    
    if not Path(reports_dir).exists():
        print(f"❌ Erro: Pasta não encontrada: {reports_dir}")
        print("   Crie a pasta e adicione arquivos PDF para análise.")
        return
    
    # Inicializa o processador
    print("🔧 Inicializando analisador...")
    processor = PDFSentimentProcessor(
        positive_words_path=positive_words_path,
        negative_words_path=negative_words_path
    )
    
    # Processa todos os arquivos
    print(f"📁 Processando arquivos em: {reports_dir}")
    results = processor.process_all_pdfs(reports_dir)
    
    if not results:
        print("❌ Nenhum arquivo foi processado com sucesso.")
        print("   Verifique se há arquivos PDF na pasta relatorios_empresas.")
        return
    
    # Salva os resultados (substitui se já existir)
    print("\n💾 Salvando relatórios...")
    saved_files = processor.save_results(results, output_dir="outputs")
    
    # Exibe resumo
    summary = processor.generate_report_summary(results)
    print(f"\n📊 === RESUMO FINAL ===")
    print(f"✅ Total de arquivos processados: {summary['total_files']}")
    print(f"📈 Média de palavras positivas: {summary['avg_positive']:.4f}")
    print(f"📉 Média de palavras negativas: {summary['avg_negative']:.4f}")
    print(f"📝 Total de palavras processadas: {summary['total_words_processed']}")
    print(f"😊 Total de palavras positivas: {summary['total_positive_count']}")
    print(f"😞 Total de palavras negativas: {summary['total_negative_count']}")
    
    print(f"\n🎉 RELATÓRIO GERADO COM SUCESSO!")
    print(f"📂 Relatórios CSV salvos em {len(saved_files)} pastas:")
    for i, (pos_file, neg_file) in enumerate(saved_files, 1):
        folder_name = Path(pos_file).parent.name
        print(f"   {i}. {folder_name}/")
        print(f"      ├── resultado_positivo.csv")
        print(f"      └── resultado_negativo.csv")
    
    print(f"\n💡 Dica: Os arquivos foram salvos/substituídos em outputs/")
    print(f"   Cada PDF tem sua própria pasta com os resultados em CSV.")
    
    # Mostra o caminho absoluto
    import os
    abs_output_path = os.path.abspath("outputs")
    print(f"\n📍 Caminho absoluto: {abs_output_path}")
    print(f"📂 Verifique a pasta: {abs_output_path}")


if __name__ == "__main__":
    main()
