@echo off
setlocal
chcp 65001 >NUL
title TIBIA BAGUA - Servidor Local

set "OTCDIR=%~dp0TIBIA BAGUA\otclient-src"
set "LOGINDIR=%~dp0TIBIA BAGUA\login-server-src"
set "CANARYDIR=C:\dev\canary_run"
set "PROFILE=C:/dev/otcprofile"

echo ==========================================
echo    TIBIA BAGUA - Iniciando servidor local
echo ==========================================
echo.

echo [1/4] MySQL...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I "mysqld.exe" >NUL
if errorlevel 1 (
  start "" /B "C:\xampp\mysql\bin\mysqld.exe" --defaults-file=C:\xampp\mysql\bin\my.ini --standalone
  echo       iniciado, aguardando...
  ping -n 9 127.0.0.1 >NUL
) else (
  echo       ja estava rodando.
)

echo [2/4] Servidor Canary...
tasklist /FI "IMAGENAME eq canary.exe" 2>NUL | find /I "canary.exe" >NUL
if errorlevel 1 (
  start "Canary" /D "%CANARYDIR%" /MIN "%CANARYDIR%\canary.exe"
  echo       iniciado, carregando o mundo ^(pode levar ~25s^)...
  ping -n 29 127.0.0.1 >NUL
) else (
  echo       ja estava rodando.
)

echo [3/4] Login server...
tasklist /FI "IMAGENAME eq login-server-new.exe" 2>NUL | find /I "login-server-new.exe" >NUL
if errorlevel 1 (
  start "LoginServer" /D "%LOGINDIR%" /MIN "%LOGINDIR%\login-server-new.exe"
  ping -n 6 127.0.0.1 >NUL
  echo       iniciado.
) else (
  echo       ja estava rodando.
)

echo [4/4] Abrindo o jogo...
start "" /D "%OTCDIR%" "%OTCDIR%\otclient.exe" --user-dir=%PROFILE%

echo.
echo Pronto! O cliente vai entrar no mundo automaticamente com o personagem Admin.
echo Conta: admin  ^|  Senha: admin123
echo.
ping -n 7 127.0.0.1 >NUL
endlocal
