@echo off
setlocal

set ARCHIVE_NAME=package.zip
cd "%~dp0"

REM Common root directory
set ROOT_DIR=..\..

REM Paths to include (relative to ROOT_DIR)
set REL_DIR1=src\multi-chat\node_modules
set REL_DIR2=src\multi-chat\vendor
set REL_DIR3=windows\packages

REM Create zip using 7-Zip
if "%1"=="zip" (
    echo Creating archive %ARCHIVE_NAME% using 7-Zip from %ROOT_DIR%...
    pushd %ROOT_DIR%
    7z a -tzip "scripts/windows-setup-files/%ARCHIVE_NAME%" "%REL_DIR1%" "%REL_DIR2%" "%REL_DIR3%"
    popd
    goto :eof
)

REM Restore using native tar to ../../
if "%1"=="restore" (
    echo Restoring from archive %ARCHIVE_NAME% to ../../ using native tar...
    tar -xf "%ARCHIVE_NAME%" -C ..\..
    goto :eof
)

echo Usage: %0 ^<zip^|restore^>
endlocal
