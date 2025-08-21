$ErrorActionPreference = 'Stop'

Write-Output "=== Instalação do Analisador de Notícias (Windows) ==="

# 1) Garantir Python 3 instalado
$hasPython = (Get-Command python -ErrorAction SilentlyContinue) -ne $null -or \
             (Get-Command python3 -ErrorAction SilentlyContinue) -ne $null -or \
             (Get-Command py -ErrorAction SilentlyContinue) -ne $null

if (-not $hasPython) {
  Write-Output "🐍 Python 3 não encontrado. Instalando automaticamente..."
  if (Test-Path 'scripts\install_python_windows.ps1') {
    PowerShell.exe -ExecutionPolicy Bypass -File 'scripts\install_python_windows.ps1'
  } else {
    Write-Output "Instalador não encontrado. Tentando winget..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
      winget install --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements -e --silent
    } else {
      throw "winget não disponível. Instale Python manualmente e rode novamente."
    }
  }
}

function Resolve-Python {
  $cmds = @('python', 'python3')
  foreach ($c in $cmds) {
    $p = Get-Command $c -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
  }
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    try { return (& py -3 -c "import sys;print(sys.executable)") } catch {}
  }
  throw "Python não encontrado mesmo após instalação. Feche e reabra o PowerShell e tente novamente."
}

$pythonExe = Resolve-Python
Write-Output ("✅ Python encontrado: " + (& $pythonExe --version))

# 2) Criar venv se não existir
if (-not (Test-Path '.\.venv')) {
  Write-Output '📦 Criando ambiente virtual (.venv)...'
  & $pythonExe -m venv .venv
}

$venvPython = Join-Path '.\.venv\Scripts' 'python.exe'
if (-not (Test-Path $venvPython)) {
  throw 'Falha ao criar o ambiente virtual (.venv).'
}

# 3) Atualizar pip e instalar dependências
Write-Output '⬆️  Atualizando pip...'
& $venvPython -m pip install --upgrade pip

Write-Output '📚 Instalando dependências (requirements.txt)...'
& $venvPython -m pip install -r requirements.txt

Write-Output ''
Write-Output '🎉 Instalação concluída!'
Write-Output ''
Write-Output 'Para gerar o relatório:'
Write-Output '  - PowerShell:'
Write-Output '      .\.venv\Scripts\Activate.ps1'
Write-Output '      python -m csr_analyzer.cli run'
Write-Output '  - Ou use o atalho .bat:'
Write-Output '      .\gerar_relatorio.bat'


