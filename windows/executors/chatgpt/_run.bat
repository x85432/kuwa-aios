pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:openai/gpt
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:openai/gpt" "ChatGPT" --image "..\..\windows\executors\chatgpt\chatgpt.png" --order "401100"
popd
start /b "" "kuwa-executor" "chatgpt" "--access_code" ".model:openai/gpt"
