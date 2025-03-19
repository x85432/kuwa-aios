pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/agent
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/agent" "Agent" --image "..\..\windows\executors\agent\agent.png"
popd
pushd ..\..\..\src\executor\agent
start /b "" "python" main.py "--access_code" ".model/agent" "--log" "debug"
popd
