"""
Analisador de sentimento baseado em léxico para análise de PDFs.
Utiliza as listas de palavras positivas e negativas fornecidas.
"""

import re
import os
from typing import List, Dict, Tuple, Set
from pathlib import Path
import csv


class LexiconSentimentAnalyzer:
    """Analisador de sentimento baseado em léxico com tokenização e remoção de stop words."""
    
    def __init__(self, positive_words_path: str, negative_words_path: str):
        """Inicializa o analisador carregando as palavras positivas e negativas."""
        self.positive_words = self._load_words(positive_words_path)
        self.negative_words = self._load_words(negative_words_path)
        
        # Stop words em português
        self.stop_words = {
            'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até', 'com', 'como',
            'da', 'das', 'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram',
            'essa', 'essas', 'esse', 'esses', 'esta', 'estamos', 'estas', 'estava', 'estavam', 'este',
            'esteja', 'estejam', 'estejamos', 'estes', 'esteve', 'estive', 'estivemos', 'estiver',
            'estivera', 'estiveram', 'estiverem', 'estivermos', 'estivesse', 'estivessem', 'estivéramos',
            'estivéssemos', 'estou', 'está', 'estão', 'eu', 'foi', 'fomos', 'for', 'fora', 'foram',
            'forem', 'formos', 'fosse', 'fossem', 'fui', 'fôramos', 'fôssemos', 'haja', 'hajam',
            'hajamos', 'havemos', 'havia', 'hei', 'houve', 'houvemos', 'houver', 'houvera', 'houveram',
            'houverei', 'houverem', 'houveremos', 'houveria', 'houveriam', 'houveríamos', 'houverá',
            'houverão', 'houveríamos', 'houvesse', 'houvessem', 'houvéramos', 'houvéssemos', 'há',
            'hão', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus',
            'minha', 'minhas', 'muito', 'na', 'nas', 'nem', 'no', 'nos', 'nossa', 'nossas', 'nosso',
            'nossos', 'num', 'numa', 'não', 'nós', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo',
            'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'se', 'seja', 'sejam', 'sejamos', 'sem',
            'ser', 'seria', 'seriam', 'será', 'serão', 'seríamos', 'seu', 'seus', 'só', 'sua', 'suas',
            'são', 'são', 'só', 'também', 'te', 'tem', 'temos', 'tenha', 'tenham', 'tenhamos', 'tenho',
            'ter', 'terei', 'teremos', 'teria', 'teriam', 'terá', 'terão', 'teríamos', 'teve', 'tinha',
            'tinham', 'tive', 'tivemos', 'tiver', 'tivera', 'tiveram', 'tiverem', 'tivermos', 'tivesse',
            'tivessem', 'tivéramos', 'tivéssemos', 'tu', 'tua', 'tuas', 'tém', 'tínhamos', 'um', 'uma',
            'você', 'vocês', 'vos', 'à', 'às', 'éramos', 'é', 'são', 'só', 'também', 'te', 'tem', 'temos',
            'tenha', 'tenham', 'tenhamos', 'tenho', 'ter', 'terei', 'teremos', 'teria', 'teriam', 'terá',
            'terão', 'teríamos', 'teve', 'tinha', 'tinham', 'tive', 'tivemos', 'tiver', 'tivera', 'tiveram',
            'tiverem', 'tivermos', 'tivesse', 'tivessem', 'tivéramos', 'tivéssemos', 'tu', 'tua', 'tuas',
            'tém', 'tínhamos', 'um', 'uma', 'você', 'vocês', 'vos', 'à', 'às', 'éramos'
        }
    
    def _load_words(self, words_path: str) -> Set[str]:
        """Carrega palavras de um arquivo CSV."""
        words = set()
        try:
            with open(words_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].strip():
                        words.add(row[0].strip().lower())
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {words_path}")
        return words
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza o texto removendo pontuação e convertendo para minúsculas."""
        # Remove pontuação e quebra em palavras
        text = re.sub(r'[^\w\s]', ' ', text)
        # Converte para minúsculas e divide em palavras
        tokens = text.lower().split()
        return tokens
    
    def _remove_stop_words(self, tokens: List[str]) -> List[str]:
        """Remove stop words da lista de tokens."""
        return [token for token in tokens if token not in self.stop_words and len(token) > 2]
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analisa o sentimento do texto.
        
        Returns:
            Dict com 'positive', 'negative' e 'total_words'
        """
        if not text or not text.strip():
            return {'positive': 0.0, 'negative': 0.0, 'total_words': 0}
        
        # Tokenização e remoção de stop words
        tokens = self._tokenize(text)
        filtered_tokens = self._remove_stop_words(tokens)
        
        if not filtered_tokens:
            return {'positive': 0.0, 'negative': 0.0, 'total_words': 0}
        
        # Contagem de palavras positivas e negativas
        positive_count = sum(1 for token in filtered_tokens if token in self.positive_words)
        negative_count = sum(1 for token in filtered_tokens if token in self.negative_words)
        total_words = len(filtered_tokens)
        
        # Cálculo das proporções
        positive_ratio = positive_count / total_words if total_words > 0 else 0.0
        negative_ratio = negative_count / total_words if total_words > 0 else 0.0
        
        return {
            'positive': positive_ratio,
            'negative': negative_ratio,
            'total_words': total_words,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def analyze_pdf(self, pdf_path: str) -> Dict[str, float]:
        """Analisa o sentimento de um arquivo PDF."""
        try:
            from .pdf_utils import extract_text_from_pdf
            text = extract_text_from_pdf(pdf_path)
            return self.analyze_sentiment(text)
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_path}: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'total_words': 0}
