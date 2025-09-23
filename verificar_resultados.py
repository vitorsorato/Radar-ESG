#!/usr/bin/env python3
"""
Script para verificar e mostrar os resultados gerados em outputs/
"""

import os
import sys
from pathlib import Path

def main():
    """Mostra os resultados gerados e abre a pasta outputs."""
    print("🔍 VERIFICANDO RESULTADOS")
    print("=" * 40)
    
    # Caminho absoluto da pasta outputs
    outputs_path = Path("outputs").absolute()
    
    print(f"📂 Pasta outputs: {outputs_path}")
    
    if not outputs_path.exists():
        print("❌ Pasta outputs não encontrada!")
        print("   Execute primeiro: python gerar_relatorio_sentimento.py")
        return
    
    # Lista todas as pastas em outputs
    folders = [f for f in outputs_path.iterdir() if f.is_dir()]
    
    if not folders:
        print("❌ Nenhuma pasta encontrada em outputs/")
        print("   Execute primeiro: python gerar_relatorio_sentimento.py")
        return
    
    print(f"\n📁 Encontradas {len(folders)} pastas com resultados:")
    
    total_csvs = 0
    for folder in sorted(folders):
        print(f"\n📂 {folder.name}/")
        
        # Lista arquivos CSV na pasta
        csv_files = list(folder.glob("*.csv"))
        total_csvs += len(csv_files)
        
        for csv_file in csv_files:
            print(f"   📄 {csv_file.name}")
            
            # Mostra conteúdo do CSV
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    lines = content.split('\n')
                    if len(lines) >= 2:
                        print(f"      {lines[1]}")
            except Exception as e:
                print(f"      ❌ Erro ao ler arquivo: {e}")
    
    print(f"\n✅ Total: {total_csvs} arquivos CSV gerados")
    
    # Verifica se existe o arquivo consolidado
    consolidated_file = outputs_path / "resultado_geral.csv"
    if consolidated_file.exists():
        print(f"\n📊 Arquivo consolidado encontrado:")
        print(f"   📄 {consolidated_file.name}")
        try:
            with open(consolidated_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   📈 {len(lines)-1} empresas analisadas")
                print(f"   📝 {len(lines)} linhas total (incluindo cabeçalho)")
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")
    
    print(f"\n📍 Localização: {outputs_path}")
    
    # Tenta abrir a pasta no explorador de arquivos
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{outputs_path}'")
            print("🚀 Pasta aberta no Finder")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer '{outputs_path}'")
            print("🚀 Pasta aberta no Explorer")
        elif sys.platform == "linux":  # Linux
            os.system(f"xdg-open '{outputs_path}'")
            print("🚀 Pasta aberta no gerenciador de arquivos")
    except Exception as e:
        print(f"⚠️  Não foi possível abrir a pasta automaticamente: {e}")
        print(f"   Abra manualmente: {outputs_path}")

if __name__ == "__main__":
    main()
