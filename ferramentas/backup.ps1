# Cria um snapshot com data/hora dos arquivos que a edicao pode quebrar.
# O caminho do projeto vem do .bat (%~dp0) para nao depender de acentos no script.
param([string]$Projeto = "")
$ErrorActionPreference = "Stop"

$RAIZ    = "C:\dev\backups"
$MAPA    = "C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm"
$APPSRV  = "C:\dev\canary_run\data\items\appearances.dat"
if (-not $Projeto) { $Projeto = "C:\Users\lleo_\OneDrive" }
$THINGS  = Join-Path $Projeto "TIBIA BAGUA\otclient-src\data\things\1525"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   BACKUP - TIBIA BAGUA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$dest  = Join-Path $RAIZ $stamp
if (Test-Path $dest) { $dest = "$dest-" + (Get-Date -Format "ss") }
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$itens = @()
function Guardar($origem, $subpasta, $rotulo) {
    if (-not (Test-Path $origem)) {
        Write-Host ("  [!] nao encontrado: {0}" -f $rotulo) -ForegroundColor Yellow
        return
    }
    $pasta = Join-Path $dest $subpasta
    New-Item -ItemType Directory -Force -Path $pasta | Out-Null
    $mb = [math]::Round((Get-Item $origem).Length / 1MB, 1)
    Write-Host ("  copiando {0} ({1} MB)..." -f $rotulo, $mb)
    Copy-Item $origem -Destination $pasta -Force
    $script:itens += $rotulo
}

Guardar $MAPA   "mapa"      "mapa otservbr.otbm"
Guardar $APPSRV "servidor"  "appearances.dat (servidor)"

$appCli = Get-ChildItem "$THINGS\appearances-*.dat" -ErrorAction SilentlyContinue |
          Where-Object { $_.Name -notlike "*backup*" } | Select-Object -First 1
if ($appCli) { Guardar $appCli.FullName "cliente" "appearances (cliente)" }
Guardar "$THINGS\catalog-content.json" "cliente" "catalog-content.json"

# spritesheets: e o que o passo "compilar" reescreve
$sheets = Get-ChildItem "$THINGS\sprites-*.bmp.lzma" -ErrorAction SilentlyContinue
if ($sheets) {
    $totalMb = [math]::Round((($sheets | Measure-Object Length -Sum).Sum) / 1MB, 0)
    Write-Host ""
    Write-Host ("  Spritesheets: {0} arquivos, {1} MB." -f $sheets.Count, $totalMb)
    $r = Read-Host "  Incluir no backup? (demora mais) [s/N]"
    if ($r -match '^[sSyY]') {
        $pasta = Join-Path $dest "cliente\sprites"
        New-Item -ItemType Directory -Force -Path $pasta | Out-Null
        Write-Host "  copiando spritesheets..."
        $sheets | Copy-Item -Destination $pasta -Force
        $script:itens += "spritesheets ($($sheets.Count) arquivos)"
    }
}

$tam = [math]::Round((Get-ChildItem $dest -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ""
Write-Host "Backup criado:" -ForegroundColor Green
Write-Host "  $dest"
Write-Host ("  {0} MB  |  {1}" -f $tam, ($itens -join ", "))
Write-Host ""

$todos = Get-ChildItem $RAIZ -Directory -ErrorAction SilentlyContinue
if ($todos.Count -gt 1) {
    $soma = [math]::Round((Get-ChildItem $RAIZ -Recurse -File | Measure-Object Length -Sum).Sum / 1GB, 2)
    Write-Host ("Voce tem {0} backups ocupando {1} GB em {2}" -f $todos.Count, $soma, $RAIZ) -ForegroundColor DarkGray
}
$livre = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Host ("Espaco livre em C: {0} GB" -f $livre) -ForegroundColor DarkGray
Write-Host ""
Write-Host "Para voltar atras, rode RESTAURAR.bat" -ForegroundColor Cyan
Write-Host ""
Read-Host "Enter para fechar"
