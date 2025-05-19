@echo off
cd "%~dp0"
setlocal enabledelayedexpansion
rem Initialize the CUDA version variable
set "version=cpu"

rem Check if the version parameter is provided
if not "%1"=="" (
    set "set_version=%1"
)

if "!set_version!"=="" (
	rem Check if nvcc (NVIDIA CUDA Compiler) is available
	nvcc --version >NUL
	if !errorlevel! neq 0 (
		echo CUDA is not installed
	) else (
		for /f "tokens=6" %%v in ('nvcc --version ^| findstr /i "release"') do (
			set "cuda_version=%%v"
		)
		echo Found CUDA !cuda_version! installed.
		set "version=cu118"
	)
) else (
	set "version=!set_version!"
)
echo Picked version: !version!
xcopy /s /e /i /Y version_patch\!version!\* ..\..\
endlocal