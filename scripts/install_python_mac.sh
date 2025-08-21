#!/bin/bash
set -e

if command -v python3 &>/dev/null; then
  echo "Python já está instalado: $(python3 --version)"; exit 0; fi

if ! command -v brew &>/dev/null; then
  echo "Homebrew não encontrado. Instalando Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo 'eval "$('/opt/homebrew/bin/brew' shellenv)"' >> ~/.zprofile
  eval "$('/opt/homebrew/bin/brew' shellenv)"
fi

echo "Instalando Python 3 via Homebrew..."
brew update
brew install python@3.11

echo "✅ Python instalado: $(python3 --version)"
