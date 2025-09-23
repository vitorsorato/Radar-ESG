@echo off
REM Script para gerar relatório de sentimento de todos os PDFs
REM em relatorios_empresas

echo 🚀 Iniciando análise de sentimento...
echo ======================================

REM Verifica se o Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

REM Executa o script Python
python gerar_relatorio_sentimento.py

echo.
echo ✅ Processo concluído!
echo 📁 Verifique os resultados na pasta outputs/
pause
