$ErrorActionPreference = 'Stop'

# Check if Python exists
$python = Get-Command python -ErrorAction SilentlyContinue
$python3 = Get-Command python3 -ErrorAction SilentlyContinue

if ($python -or $python3) {
  Write-Output "Python já está instalado."; exit 0
}

# Try winget
$winget = Get-Command winget -ErrorAction SilentlyContinue
if ($winget) {
  Write-Output "Instalando Python via winget..."
  winget install --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements -e --silent
  Write-Output "Concluído. Reinicie o terminal se necessário."
  exit 0
}

# Fallback: download installer
$temp = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine($env:TEMP, "python_install")) -Force
$msi = Join-Path $temp.FullName "python-installer.exe"
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $msi

Write-Output "Executando instalador silencioso..."
Start-Process -FilePath $msi -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait

Write-Output "✅ Python instalado. Feche e reabra o PowerShell para aplicar PATH."
