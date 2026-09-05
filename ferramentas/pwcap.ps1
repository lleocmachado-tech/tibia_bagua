# Captura o conteudo de uma janela via PrintWindow (nao precisa de foco).
# Nao funciona para canvas OpenGL (sai preto).
param(
  [Parameter(Mandatory=$true)][string]$Proc,
  [Parameter(Mandatory=$true)][string]$Out,
  [string]$TitleMatch = ""
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;using System.Runtime.InteropServices;
public class Pw {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  public struct R { public int L,T,Rr,B; }
}
"@
$p = Get-Process $Proc -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowHandle -ne 0 -and ($TitleMatch -eq "" -or $_.MainWindowTitle -like "*$TitleMatch*") } |
     Sort-Object { $_.MainWindowTitle.Length } -Descending |
     Select-Object -First 1
if (-not $p) { Write-Output "ERRO: '$Proc' nao encontrado"; exit 1 }
$h = $p.MainWindowHandle
$r = New-Object Pw+R
[Pw]::GetWindowRect($h,[ref]$r) | Out-Null
$w = $r.Rr-$r.L; $ht = $r.B-$r.T
$bmp = New-Object System.Drawing.Bitmap($w,$ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc(); [Pw]::PrintWindow($h,$dc,2) | Out-Null; $g.ReleaseHdc($dc)
$bmp.Save($Out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "OK: $Out (${w}x${ht}) titulo='$($p.MainWindowTitle)'"
