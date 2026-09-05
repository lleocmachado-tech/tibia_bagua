# Helper: traz uma janela para frente de forma confiavel e captura a tela dela.
# Uso: .\wincap.ps1 -Proc "nome" -Out "C:\dev\x.png" [-Keys "^g"] [-Maximize]

param(
  [Parameter(Mandatory=$true)][string]$Proc,
  [Parameter(Mandatory=$true)][string]$Out,
  [int]$WaitBefore = 2,
  [switch]$Maximize
)

Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Fg {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  public struct R { public int L, T, Rr, B; }
}
"@

$p = Get-Process $Proc -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "ERRO: processo '$Proc' sem janela visivel"; exit 1 }
$h = $p.MainWindowHandle

# Trick: anexa o input thread para que SetForegroundWindow nao seja bloqueado.
# Repete ate confirmar, porque outra janela pode roubar o foco no meio.
$myThread = [Fg]::GetCurrentThreadId()
$now = [IntPtr]::Zero
for ($try = 1; $try -le 12; $try++) {
  $fgWin = [Fg]::GetForegroundWindow()
  $fgThread = [Fg]::GetWindowThreadProcessId($fgWin, [IntPtr]::Zero)
  [Fg]::AttachThreadInput($fgThread, $myThread, $true) | Out-Null
  if ($Maximize) { [Fg]::ShowWindow($h, 3) | Out-Null } else { [Fg]::ShowWindow($h, 9) | Out-Null }
  [Fg]::BringWindowToTop($h) | Out-Null
  [Fg]::SetForegroundWindow($h) | Out-Null
  [Fg]::AttachThreadInput($fgThread, $myThread, $false) | Out-Null
  Start-Sleep -Milliseconds 700
  $now = [Fg]::GetForegroundWindow()
  if ($now -eq $h) { break }
}

Start-Sleep -Seconds $WaitBefore
$now = [Fg]::GetForegroundWindow()
if ($now -ne $h) {
  Write-Output "AVISO: a janela alvo NAO esta em primeiro plano (fg=$now alvo=$h) - captura pode sair errada"
}

$r = New-Object Fg+R
[Fg]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Rr - $r.L; $ht = $r.B - $r.T
if ($w -le 0 -or $ht -le 0) { Write-Output "ERRO: rect invalido"; exit 1 }

$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size($w, $ht)))
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "OK: $Out (${w}x${ht}) foreground=$($now -eq $h)"
