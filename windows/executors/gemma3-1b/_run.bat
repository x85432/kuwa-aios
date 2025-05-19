pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/google/gemma-3-1b
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/google/gemma-3-1b" "Gemma 3 1B" --image "..\..\windows\executors\gemma3-1b\gemma-3-1b.png" --order "311003"
popd
start /b "" "kuwa-executor" "llamacpp" "--access_code" ".model/google/gemma-3-1b" "--ngl" "-1" "--model_path" "gemma-3-1b-it-q4_0.gguf"
