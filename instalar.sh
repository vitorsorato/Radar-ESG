#!/bin/bash
# Script de instalação simples (instala Python se necessário)
set -e

echo "=== Instalação do Analisador de Notícias ==="
echo ""

# Detectar/instalar Python automaticamente
if ! command -v python3 &> /dev/null; then
    echo "🐍 Python 3 não encontrado. Instalando automaticamente..."
    OS_NAME="$(uname -s 2>/dev/null || echo Unknown)"
    case "$OS_NAME" in
        Darwin)
            if [ -x "./scripts/install_python_mac.sh" ]; then
                bash ./scripts/install_python_mac.sh
            else
                echo "Instalador do macOS não encontrado. Tentando via Homebrew..."
                if ! command -v brew &>/dev/null; then
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    echo 'eval "$('/opt/homebrew/bin/brew' shellenv)"' >> ~/.zprofile
                    eval "$('/opt/homebrew/bin/brew' shellenv)"
                fi
                brew update && brew install python@3.11
            fi
            ;;
        Linux)
            if [ -x "./scripts/install_python_ubuntu.sh" ]; then
                bash ./scripts/install_python_ubuntu.sh
            else
                if command -v apt-get &>/dev/null; then
                    sudo apt-get update -y
                    sudo apt-get install -y python3 python3-venv python3-pip
                else
                    echo "Distribuição Linux não suportada automaticamente. Instale Python 3 e rode novamente."
                    exit 1
                fi
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            if command -v powershell.exe &>/dev/null; then
                powershell.exe -ExecutionPolicy Bypass -File scripts\\install_python_windows.ps1
            else
                echo "Windows detectado. Execute scripts\\install_python_windows.ps1 no PowerShell (Admin)."
                exit 1
            fi
            ;;
        *)
            echo "Sistema operacional não detectado automaticamente. Instale Python 3 e rode novamente."
            exit 1
            ;;
    esac
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
python -m pip install --upgrade pip -q

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt -q

echo ""
echo "🎉 Instalação concluída!"
echo ""
echo "Para usar:"
echo "  1. Execute: source .venv/bin/activate"
echo "  2. Execute: ./gerar_relatorio.sh"
echo ""

