@echo off
setlocal

set ARCHIVE_NAME=package.zip

REM Directories to include
set DIR1=..\..\src\multi-chat\node_modules
set DIR2=..\..\src\multi-chat\vendor
set DIR3=..\..\windows\packages

if "%1"=="zip" (
    echo Creating archive %ARCHIVE_NAME%...
    7z a -tzip %ARCHIVE_NAME% "%DIR1%" "%DIR2%" "%DIR3%"
    goto :eof
)

if "%1"=="restore" (
    echo Restoring from archive %ARCHIVE_NAME%...
    7z x %ARCHIVE_NAME% -aoa
    goto :eof
)

echo Usage: %0 ^<zip^|restore^>
endlocal
