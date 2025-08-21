@echo off
setlocal

if not exist .\.venv (
  echo Ambiente virtual nao encontrado. Execute instalar.ps1 primeiro.
  exit /b 1
)

call .\.venv\Scripts\activate.bat
python -m csr_analyzer.cli run

if %errorlevel% neq 0 (
  echo Erro ao gerar relatorio
  exit /b %errorlevel%
)

echo Relatorio gerado em outputs\relatorio_noticias.pdf
endlocal

