"""
Processador de PDFs para análise de sentimento.
Processa todos os PDFs na pasta relatorios_empresas e gera relatórios de sentimento.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from .lexicon_sentiment import LexiconSentimentAnalyzer


class PDFSentimentProcessor:
    """Processador de PDFs para análise de sentimento."""
    
    def __init__(self, 
                 positive_words_path: str = "data/palavras_positivas.csv",
                 negative_words_path: str = "data/palavras_negativas.csv"):
        """Inicializa o processador com os caminhos dos arquivos de palavras."""
        self.analyzer = LexiconSentimentAnalyzer(positive_words_path, negative_words_path)
    
    def find_pdf_files(self, directory: str) -> List[str]:
        """Encontra todos os arquivos PDF e TXT no diretório especificado."""
        files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"Diretório não encontrado: {directory}")
            return files
        
        # Busca por PDFs e TXTs (para testes)
        for file_path in directory_path.rglob("*.pdf"):
            files.append(str(file_path))
        for file_path in directory_path.rglob("*.txt"):
            files.append(str(file_path))
        
        return files
    
    def process_pdf(self, file_path: str) -> Dict[str, float]:
        """Processa um único arquivo (PDF ou TXT) e retorna os resultados de sentimento."""
        file_name = Path(file_path).name
        print(f"📄 Processando: {file_name}")
        
        # Verifica se é um arquivo de texto
        if file_path.lower().endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                results = self.analyzer.analyze_sentiment(text)
                print(f"   📝 Arquivo de texto lido com sucesso")
            except Exception as e:
                print(f"   ❌ Erro ao ler arquivo de texto: {e}")
                results = {'positive': 0.0, 'negative': 0.0, 'total_words': 0}
        else:
            # Processa como PDF
            try:
                results = self.analyzer.analyze_pdf(file_path)
                if results['total_words'] > 0:
                    print(f"   📄 PDF processado com sucesso")
                else:
                    print(f"   ⚠️  PDF processado mas nenhum texto extraído")
            except Exception as e:
                print(f"   ❌ Erro ao processar PDF: {e}")
                results = {'positive': 0.0, 'negative': 0.0, 'total_words': 0}
        
        # Adiciona informações do arquivo
        results['file_name'] = file_name
        results['file_path'] = file_path
        
        # Garante que os campos de contagem existem
        if 'positive_count' not in results:
            results['positive_count'] = 0
        if 'negative_count' not in results:
            results['negative_count'] = 0
        
        # Log dos resultados
        if results['total_words'] > 0:
            pos_pct = results['positive'] * 100
            neg_pct = results['negative'] * 100
            print(f"   ✅ Extraído: {results['total_words']:,} palavras")
            print(f"   😊 Positivo: {pos_pct:.2f}% ({results['positive_count']:,} palavras)")
            print(f"   😞 Negativo: {neg_pct:.2f}% ({results['negative_count']:,} palavras)")
        else:
            print(f"   ⚠️  Nenhuma palavra processada")
        
        return results
    
    def process_all_pdfs(self, directory: str = "relatorios_empresas") -> List[Dict[str, float]]:
        """Processa todos os arquivos (PDFs e TXTs) no diretório especificado."""
        files = self.find_pdf_files(directory)
        
        if not files:
            print(f"❌ Nenhum arquivo encontrado em: {directory}")
            return []
        
        print(f"📁 Encontrados {len(files)} arquivos para processar")
        print("=" * 60)
        
        results = []
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] ", end="")
            try:
                result = self.process_pdf(file_path)
                results.append(result)
            except Exception as e:
                print(f"❌ Erro crítico ao processar {file_path}: {e}")
                # Adiciona resultado vazio para manter consistência
                results.append({
                    'file_name': Path(file_path).name,
                    'positive': 0.0,
                    'negative': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'total_words': 0
                })
        
        print("\n" + "=" * 60)
        return results
    
    def generate_report_summary(self, results: List[Dict[str, float]]) -> Dict[str, float]:
        """Gera um resumo dos resultados de todos os PDFs processados."""
        if not results:
            return {'avg_positive': 0.0, 'avg_negative': 0.0, 'total_files': 0}
        
        total_positive = sum(r['positive'] for r in results)
        total_negative = sum(r['negative'] for r in results)
        total_files = len(results)
        
        return {
            'avg_positive': total_positive / total_files,
            'avg_negative': total_negative / total_files,
            'total_files': total_files,
            'total_positive_count': sum(r['positive_count'] for r in results),
            'total_negative_count': sum(r['negative_count'] for r in results),
            'total_words_processed': sum(r['total_words'] for r in results)
        }
    
    def save_results(self, results: List[Dict[str, float]], 
                    output_dir: str = "outputs") -> List[Tuple[str, str]]:
        """
        Salva os resultados em arquivos CSV separados para cada arquivo processado.
        Cria uma pasta para cada arquivo com o nome do arquivo (sem extensão).
        Também gera um arquivo consolidado com todos os resultados.
        
        Returns:
            Lista de tuplas com os caminhos dos arquivos de resultado positivo e negativo
        """
        import csv
        
        saved_files = []
        
        for result in results:
            # Remove a extensão do nome do arquivo para criar o nome da pasta
            file_name = Path(result['file_name']).stem
            file_folder = Path(output_dir) / file_name
            file_folder.mkdir(parents=True, exist_ok=True)
            
            # Arquivo CSV de resultado positivo
            positive_file = file_folder / "resultado_positivo.csv"
            with open(positive_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Arquivo', 'Proporção_Positiva', 'Contagem_Positiva', 'Total_Palavras'])
                writer.writerow([
                    result['file_name'],
                    f"{result['positive']:.6f}",
                    result['positive_count'],
                    result['total_words']
                ])
            
            # Arquivo CSV de resultado negativo
            negative_file = file_folder / "resultado_negativo.csv"
            with open(negative_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Arquivo', 'Proporção_Negativa', 'Contagem_Negativa', 'Total_Palavras'])
                writer.writerow([
                    result['file_name'],
                    f"{result['negative']:.6f}",
                    result['negative_count'],
                    result['total_words']
                ])
            
            saved_files.append((str(positive_file), str(negative_file)))
        
        print(f"\n💾 Salvando relatórios...")
        for result in results:
            file_name = Path(result['file_name']).stem
            print(f"✓ Relatórios salvos para {result['file_name']}:")
            print(f"  - Positivo: outputs/{file_name}/resultado_positivo.csv")
            print(f"  - Negativo: outputs/{file_name}/resultado_negativo.csv")
        
        # Gera arquivo consolidado com todos os resultados
        self._save_consolidated_results(results, output_dir)
        
        return saved_files
    
    def _save_consolidated_results(self, results: List[Dict[str, float]], output_dir: str):
        """
        Salva um arquivo consolidado com todos os resultados em uma única tabela.
        """
        import csv
        
        consolidated_file = Path(output_dir) / "resultado_geral.csv"
        
        with open(consolidated_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow([
                'Arquivo', 
                'Proporção_Positiva', 
                'Contagem_Positiva', 
                'Proporção_Negativa', 
                'Contagem_Negativa', 
                'Total_Palavras'
            ])
            
            # Dados de cada arquivo
            for result in results:
                writer.writerow([
                    result['file_name'],
                    f"{result['positive']:.6f}",
                    result['positive_count'],
                    f"{result['negative']:.6f}",
                    result['negative_count'],
                    result['total_words']
                ])
        
        print(f"\n📊 Arquivo consolidado gerado: {consolidated_file}")
        print(f"   Contém todos os {len(results)} resultados em uma única tabela")
