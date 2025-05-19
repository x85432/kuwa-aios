pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:nim/
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:nim/" "NIM API" --image "..\..\windows\executors\nim\nim.png" --order "401200"
popd
start /b "" "kuwa-executor" "nim" "--access_code" ".model:nim/"
