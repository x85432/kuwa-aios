pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/agent
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/agent" "Agent" --order=999010 --image "..\..\windows\executors\agent\agent.png"
popd
pushd ..\..\..\src\executor\agent
for /L %%a in (1,1,5) do (
start /b "" "python" main.py "--access_code" ".tool/kuwa/agent" "--log" "debug"
)
popd
