@echo off
pushd ..\..\src
call variables.bat
popd

python prepare_qnn.py