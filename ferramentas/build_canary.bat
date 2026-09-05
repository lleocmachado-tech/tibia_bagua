@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
set "PATH=C:\dev\canary\.tools\vcpkg\downloads\tools\ninja-1.13.2-windows;%PATH%"
cd /d C:\dev\canary
cmake --build build/windows-release --target canary
echo BUILD_EXIT_CODE=%ERRORLEVEL%
