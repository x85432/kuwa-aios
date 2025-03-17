pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/google/gemma3-1b-it
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/google/gemma3-1b-it" "Gemma3-1B" --image "..\..\windows\executors\gemma3-1b\gemma3-1b.png"
popd
start /b "" "kuwa-executor" "huggingface" "--access_code" ".model/google/gemma3-1b-it" "--model_path" "google/gemma3-1b-it" --log debug
