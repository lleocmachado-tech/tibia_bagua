# Traz a janela para frente (confirmando) e envia teclas via SendKeys.
# So envia se confirmar que a janela alvo esta em primeiro plano.
param(
  [Parameter(Mandatory=$true)][string]$Proc,
  [Parameter(Mandatory=$true)][string]$Keys,
  [int]$DelayAfter = 2
)
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Fg2 {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@
$p = Get-Process $Proc -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "ERRO: '$Proc' nao encontrado"; exit 1 }
$h = $p.MainWindowHandle
$myThread = [Fg2]::GetCurrentThreadId()
for ($i = 1; $i -le 12; $i++) {
  $fg = [Fg2]::GetForegroundWindow()
  $ft = [Fg2]::GetWindowThreadProcessId($fg, [IntPtr]::Zero)
  [Fg2]::AttachThreadInput($ft, $myThread, $true) | Out-Null
  [Fg2]::ShowWindow($h, 9) | Out-Null
  [Fg2]::BringWindowToTop($h) | Out-Null
  [Fg2]::SetForegroundWindow($h) | Out-Null
  [Fg2]::AttachThreadInput($ft, $myThread, $false) | Out-Null
  Start-Sleep -Milliseconds 600
  if ([Fg2]::GetForegroundWindow() -eq $h) { break }
}
if ([Fg2]::GetForegroundWindow() -ne $h) {
  Write-Output "ABORTADO: nao consegui colocar '$Proc' em primeiro plano - NAO enviei teclas"
  exit 2
}
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Seconds $DelayAfter
Write-Output "OK: teclas enviadas para '$Proc' ($($p.MainWindowTitle))"
