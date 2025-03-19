pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/google/gemma-3-4b-it
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/google/gemma-3-4b-it" "Gemma3-4B" --image "..\..\windows\executors\gemma3-4b\gemma-3-4b.png"
popd
start /b "" "kuwa-executor" "huggingface" "--access_code" ".model/google/gemma-3-4b-it" "--model_path" "google/gemma-3-4b-it" --log debug
