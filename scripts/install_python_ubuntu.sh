#!/bin/bash
set -e

if command -v python3 &>/dev/null; then
  echo "Python já está instalado: $(python3 --version)"; exit 0; fi

echo "Atualizando pacotes..."
sudo apt-get update -y

echo "Instalando Python 3, venv e pip..."
sudo apt-get install -y python3 python3-venv python3-pip

echo "✅ Python instalado: $(python3 --version)"
