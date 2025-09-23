from typing import Optional
import warnings
import logging
import sys
import io

# Configura logging para suprimir warnings desnecessários
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("PyMuPDF").setLevel(logging.ERROR)

def extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None) -> str:
    """Extract text from a PDF file using multiple methods for better compatibility.

    Args:
        pdf_path: Path to a PDF file on disk.
        max_pages: Optional page limit to stop early.

    Returns:
        Full text extracted from the PDF, or empty string if extraction fails.
    """
    text = ""
    method_used = ""
    
    # Suprime warnings e erros de renderização que não afetam a extração de texto
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Captura stderr para suprimir mensagens de erro de renderização
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        try:
            # Method 1: Try pypdf first
            try:
                from pypdf import PdfReader
                reader = PdfReader(pdf_path)
                num_pages = len(reader.pages)
                text_chunks = []
                limit = num_pages if max_pages is None else min(num_pages, max_pages)
                for page_index in range(limit):
                    page = reader.pages[page_index]
                    page_text = page.extract_text() or ""
                    text_chunks.append(page_text)
                text = "\n\n".join(text_chunks)
                if text.strip():  # If we got text, return it
                    method_used = "pypdf"
                    return text
            except Exception:
                pass  # Silently try next method
            
            # Method 2: Try pdfplumber (better for presentations)
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text_chunks = []
                    pages_to_process = pdf.pages[:max_pages] if max_pages else pdf.pages
                    for page in pages_to_process:
                        page_text = page.extract_text() or ""
                        text_chunks.append(page_text)
                    text = "\n\n".join(text_chunks)
                    if text.strip():  # If we got text, return it
                        method_used = "pdfplumber"
                        return text
            except ImportError:
                pass  # Silently try next method
            except Exception:
                pass  # Silently try next method
            
            # Method 3: Try PyMuPDF (fitz) - very robust
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(pdf_path)
                text_chunks = []
                pages_to_process = range(min(len(doc), max_pages)) if max_pages else range(len(doc))
                for page_num in pages_to_process:
                    page = doc[page_num]
                    page_text = page.get_text() or ""
                    text_chunks.append(page_text)
                doc.close()
                text = "\n\n".join(text_chunks)
                if text.strip():  # If we got text, return it
                    method_used = "PyMuPDF"
                    return text
            except ImportError:
                pass  # Silently try next method
            except Exception:
                pass  # Silently try next method
            
            # Method 4: Try pdfminer (fallback)
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(pdf_path)
                if text.strip():  # If we got text, return it
                    method_used = "pdfminer"
                    return text
            except ImportError:
                pass  # Silently try next method
            except Exception:
                pass  # Silently try next method
                
        finally:
            # Restaura stderr
            sys.stderr = old_stderr
    
    # Se chegou aqui, nenhum método funcionou
    print(f"⚠️  Não foi possível extrair texto do PDF: {pdf_path}")
    return ""
