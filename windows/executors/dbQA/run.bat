pushd "C:\kuwa\GenAI OS\windows\executors\dbQA"
call ..\..\src\variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/db-qa
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/db-qa" "dbQA" --image "..\..\windows\executors\dbQA\dbQA.png" --do_not_create_bot --order "990000"
popd
pushd ..\..\..\src\executor\docqa\
start /b "" "python" docqa.py "--access_code" ".tool/kuwa/db-qa"
popd
