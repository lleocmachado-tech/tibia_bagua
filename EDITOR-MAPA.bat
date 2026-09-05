@echo off
setlocal
title Editor de Mapa - TIBIA BAGUA

set "RME=C:\dev\tools\rme\canary-map-editor-v4.0-windows"
set "MAPA=C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm"

echo Abrindo o editor de mapa com o mapa do servidor...
echo.
echo   Mapa: otservbr.otbm  (184 MB - leva ~40s para carregar)
echo   Ele abre direto no templo de Thais (32369, 32241, 7).
echo   Ctrl+G pula para outra posicao.
echo.
echo   Antes de editar, vale rodar o BACKUP.bat.
echo.
echo   ATENCAO: o servidor le o .otbm so quando inicia.
echo   Salve no editor e reinicie o Canary para ver as mudancas no jogo.
echo.

start "" /D "%RME%" "%RME%\canary-map-editor-x64.exe" "%MAPA%"
ping -n 4 127.0.0.1 >NUL
endlocal
