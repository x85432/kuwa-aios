pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/pipe
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/pipe" "Pipe" --image "..\..\windows\executors\pipe\pipe.png"
popd
pushd ..\..\..\src\executor\pipe
start /b "" "python" main.py "--access_code" ".tool/kuwa/pipe" --log debug
popd