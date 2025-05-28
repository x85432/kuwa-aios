pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn" "Qualcomm QNN Genie" --order=110001 --image "..\..\windows\executors\qnn-genie\snapdragon-x.jpg" --do_not_create_bot
popd
pushd ..\..\..\src\executor\qnn_genie
start /b "" "python" genie-t2t-run.py "--access_code" ".model:qnn" "--qnn_binaries" "..\..\..\windows\packages\qnn-binaries" --log debug 
popd