@echo off
setlocal enabledelayedexpansion
title Editor de Sprites - TIBIA BAGUA

set "REL=C:\dev\tools\beats-editor\src-tauri\target\release"
set "LS=C:\dev\tools\libresprite"
set "TRAB=C:\dev\tools\sprites-trabalho"
set "ASSETS=C:\dev\tools\rme-assets\assets"

echo ==========================================
echo    Editor de Sprites - TIBIA BAGUA
echo ==========================================
echo.
echo   No Canary Studio, em "Client Path" clique Browse e escolha:
echo.
echo       C:\dev\tools\rme-assets
echo.
echo   (a raiz, NAO a subpasta assets)
echo.
echo   Pasta de trabalho para os PNGs: %TRAB%
echo.
echo   FLUXO:
echo     1. Canary Studio: Assets editor - ache o outfit e exporte para PNG
echo     2. LibreSprite: desenhe o PNG (sprites sao 32x32 ou 64x64)
echo     3. Canary Studio: importe o PNG de volta e compile
echo.
echo   Monster editor: C:\dev\canary_run\data-otservbr-global\monster
echo   NPC editor:     C:\dev\canary_run\data-otservbr-global\npc
echo.

set "EXE="
for %%F in ("%REL%\Canary Studio.exe" "%REL%\Canary-Studio.exe") do (
  if exist %%F set "EXE=%%~F"
)
if not defined EXE (
  for /f "delims=" %%F in ('dir /b /s "%REL%\*.exe" 2^>NUL') do (
    if not defined EXE set "EXE=%%F"
  )
)

if defined EXE (
  echo Abrindo Canary Studio...
  start "" "!EXE!"
) else (
  echo [!] Canary Studio nao encontrado em %REL%
  echo     Para recompilar: C:\dev\build_beats.bat
)

echo Abrindo LibreSprite...
start "" /D "%LS%" "%LS%\libresprite.exe"

ping -n 4 127.0.0.1 >NUL
endlocal
