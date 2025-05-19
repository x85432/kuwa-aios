pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/meta-llama/llama-3.1-8b
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/meta-llama/llama-3.1-8b" "LLaMA3.1 8B Instruct" --image "..\..\windows\executors\llama3_1\llama3_1.jpeg"
popd
start /b "" "kuwa-executor" "llamacpp" "--access_code" ".model/meta-llama/llama-3.1-8b" "--model_path" "llama3_1-8b-q4_k_m.gguf" "--ngl" "-1" "--stop" "<|eot_id|>"
