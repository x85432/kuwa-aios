pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/google/gemma
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/google/gemma" "Gemma 3 4B" --image "..\..\windows\executors\gemma3-4b\gemma-3-4b.png" "--order" "301000"
popd
start /b "" "kuwa-executor" "huggingface" "--access_code" ".model/google/gemma" "--model_path" "." "--log" "debug"
