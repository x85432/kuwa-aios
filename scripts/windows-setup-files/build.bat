@echo off
setlocal

set ARCHIVE_NAME=package.zip

REM Paths to include
set DIR1=..\..\src\multi-chat\node_modules
set DIR2=..\..\src\multi-chat\vendor
set DIR3=..\..\windows\packages

REM Create zip using 7-Zip
if "%1"=="zip" (
    echo Creating archive %ARCHIVE_NAME% using 7-Zip...
    7z a -tzip %ARCHIVE_NAME% "%DIR1%" "%DIR2%" "%DIR3%"
    goto :eof
)

REM Extract zip using native tar (Windows 10+)
if "%1"=="restore" (
    echo Restoring from archive %ARCHIVE_NAME% using native tar...
    tar -xf %ARCHIVE_NAME%
    goto :eof
)

echo Usage: %0 ^<zip^|restore^>
endlocal
