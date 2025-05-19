pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:groq/
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:groq/" "Groq API" --order=401300 --image "..\..\windows\executors\groq\groq.png" --do_not_create_bot
popd
start /b "" "kuwa-executor" "chatgpt" "--access_code" ".model:groq/" "--base_url" "https://api.groq.com/openai/v1/" "--model" "meta-llama/llama-4-maverick-17b-128e-instruct" "--context_window" "131072" "--use_third_party_api_key"
