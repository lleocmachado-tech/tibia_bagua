# Traz a janela para frente (confirmando) e clica numa coordenada RELATIVA a ela.
param(
  [Parameter(Mandatory=$true)][string]$Proc,
  [Parameter(Mandatory=$true)][int]$X,
  [Parameter(Mandatory=$true)][int]$Y,
  [switch]$Maximize,
  [int]$DelayAfter = 2
)
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Ck {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
  public struct R { public int L,T,Rr,B; }
}
"@
$p = Get-Process $Proc -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "ERRO: '$Proc' nao encontrado"; exit 1 }
$h = $p.MainWindowHandle
$my = [Ck]::GetCurrentThreadId()
for ($i=1; $i -le 12; $i++) {
  $fg = [Ck]::GetForegroundWindow(); $ft = [Ck]::GetWindowThreadProcessId($fg, [IntPtr]::Zero)
  [Ck]::AttachThreadInput($ft, $my, $true) | Out-Null
  if ($Maximize) { [Ck]::ShowWindow($h, 3) | Out-Null }
  [Ck]::BringWindowToTop($h) | Out-Null
  [Ck]::SetForegroundWindow($h) | Out-Null
  [Ck]::AttachThreadInput($ft, $my, $false) | Out-Null
  Start-Sleep -Milliseconds 600
  if ([Ck]::GetForegroundWindow() -eq $h) { break }
}
if ([Ck]::GetForegroundWindow() -ne $h) { Write-Output "ABORTADO: '$Proc' nao ficou em primeiro plano - NAO cliquei"; exit 2 }
$r = New-Object Ck+R
[Ck]::GetWindowRect($h, [ref]$r) | Out-Null
$ax = $r.L + $X; $ay = $r.T + $Y
[Ck]::SetCursorPos($ax, $ay)
Start-Sleep -Milliseconds 300
[Ck]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)  # LEFTDOWN
Start-Sleep -Milliseconds 80
[Ck]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)  # LEFTUP
Start-Sleep -Seconds $DelayAfter
Write-Output "OK: clique em ($ax,$ay) [rel $X,$Y] na janela '$($p.MainWindowTitle)'"
