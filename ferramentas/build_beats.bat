@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
set "PATH=C:\Users\lleo_\.cargo\bin;%PATH%"
cd /d C:\dev\tools\beats-editor
call npm run tauri build
echo BUILD_EXIT_CODE=%ERRORLEVEL%
