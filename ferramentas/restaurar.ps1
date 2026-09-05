# Lista os snapshots e restaura o escolhido.
# O caminho do projeto vem do .bat (%~dp0) para nao depender de acentos no script.
param([string]$Projeto = "")
$ErrorActionPreference = "Stop"

$RAIZ   = "C:\dev\backups"
$MAPA   = "C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm"
$APPSRV = "C:\dev\canary_run\data\items\appearances.dat"
if (-not $Projeto) { $Projeto = "C:\Users\lleo_\OneDrive" }
$THINGS = Join-Path $Projeto "TIBIA BAGUA\otclient-src\data\things\1525"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   RESTAURAR - TIBIA BAGUA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1) o servidor e o cliente precisam estar fechados
$abertos = Get-Process canary, otclient, "Canary-Studio", "canary-map-editor-x64" -ErrorAction SilentlyContinue
if ($abertos) {
    Write-Host "Estes programas estao abertos e travam os arquivos:" -ForegroundColor Yellow
    $abertos | ForEach-Object { Write-Host ("  - {0}" -f $_.Name) }
    Write-Host ""
    $r = Read-Host "Fechar todos agora? [S/n]"
    if ($r -notmatch '^[nN]') {
        $abertos | ForEach-Object { $_.CloseMainWindow() | Out-Null }
        Start-Sleep -Seconds 4
        Get-Process canary, otclient, "Canary-Studio", "canary-map-editor-x64" -ErrorAction SilentlyContinue |
            Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "  fechados." -ForegroundColor Green
    } else {
        Write-Host "Cancelado - feche os programas e rode de novo." -ForegroundColor Red
        Read-Host "Enter para fechar"; exit
    }
    Write-Host ""
}

# 2) escolher o snapshot
if (-not (Test-Path $RAIZ)) {
    Write-Host "Nenhum backup encontrado em $RAIZ" -ForegroundColor Yellow
    Write-Host "Rode BACKUP.bat antes de editar." -ForegroundColor Yellow
    Read-Host "Enter para fechar"; exit
}
$snaps = Get-ChildItem $RAIZ -Directory | Sort-Object Name -Descending
if (-not $snaps) {
    Write-Host "Nenhum backup encontrado." -ForegroundColor Yellow
    Read-Host "Enter para fechar"; exit
}

Write-Host "Backups disponiveis (mais recente primeiro):"
Write-Host ""
for ($i = 0; $i -lt $snaps.Count; $i++) {
    $s = $snaps[$i]
    $mb = [math]::Round((Get-ChildItem $s.FullName -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 0)
    $tem = @()
    if (Test-Path "$($s.FullName)\mapa")            { $tem += "mapa" }
    if (Test-Path "$($s.FullName)\servidor")        { $tem += "servidor" }
    if (Test-Path "$($s.FullName)\cliente")         { $tem += "cliente" }
    if (Test-Path "$($s.FullName)\cliente\sprites") { $tem += "sprites" }
    Write-Host ("  [{0}] {1}   {2,5} MB   {3}" -f ($i + 1), $s.Name, $mb, ($tem -join " + "))
}
Write-Host ""
$esc = Read-Host "Numero do backup para restaurar (Enter cancela)"
if (-not $esc) { Write-Host "Cancelado."; Read-Host "Enter para fechar"; exit }
$idx = 0
if (-not [int]::TryParse($esc, [ref]$idx) -or $idx -lt 1 -or $idx -gt $snaps.Count) {
    Write-Host "Numero invalido." -ForegroundColor Red; Read-Host "Enter para fechar"; exit
}
$snap = $snaps[$idx - 1]

Write-Host ""
Write-Host ("Isto vai SOBRESCREVER os arquivos atuais com o backup de {0}." -f $snap.Name) -ForegroundColor Yellow
$ok = Read-Host "Confirma? digite SIM"
if ($ok -ne "SIM") { Write-Host "Cancelado."; Read-Host "Enter para fechar"; exit }
Write-Host ""

function Voltar($de, $para, $rotulo) {
    if (-not (Test-Path $de)) { return }
    Copy-Item $de -Destination $para -Force
    Write-Host ("  restaurado: {0}" -f $rotulo) -ForegroundColor Green
}

$m = Get-ChildItem "$($snap.FullName)\mapa\*.otbm" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($m) { Voltar $m.FullName $MAPA "mapa otservbr.otbm" }

$a = Get-ChildItem "$($snap.FullName)\servidor\appearances.dat" -ErrorAction SilentlyContinue
if ($a) { Voltar $a.FullName $APPSRV "appearances.dat (servidor)" }

$c = Get-ChildItem "$($snap.FullName)\cliente\appearances-*.dat" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($c) { Voltar $c.FullName (Join-Path $THINGS $c.Name) "appearances (cliente)" }

$j = Get-ChildItem "$($snap.FullName)\cliente\catalog-content.json" -ErrorAction SilentlyContinue
if ($j) { Voltar $j.FullName (Join-Path $THINGS "catalog-content.json") "catalog-content.json" }

$sp = "$($snap.FullName)\cliente\sprites"
if (Test-Path $sp) {
    $n = (Get-ChildItem $sp -File).Count
    Write-Host ("  restaurando {0} spritesheets..." -f $n)
    Get-ChildItem $sp -File | Copy-Item -Destination $THINGS -Force
    Write-Host "  restaurado: spritesheets" -ForegroundColor Green
}

Write-Host ""
Write-Host "Pronto. Rode JOGAR.bat para subir o servidor de novo." -ForegroundColor Green
Write-Host ""
Read-Host "Enter para fechar"
