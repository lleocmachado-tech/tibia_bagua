@echo off
title Restaurar backup - TIBIA BAGUA
set "PS=powershell"
where pwsh >NUL 2>&1 && set "PS=pwsh"
%PS% -NoProfile -ExecutionPolicy Bypass -File "C:\dev\restaurar.ps1" -Projeto "%~dp0."
