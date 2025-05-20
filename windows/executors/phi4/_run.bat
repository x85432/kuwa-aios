pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/microsoft/phi-4-multimodal
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/microsoft/phi-4-multimodal" "Phi 4 Multimodal" --image "..\..\windows\executors\phi4\phi4.png" "--order" "301100"
popd
start /b "" "kuwa-executor" "huggingface" "--access_code" ".model/microsoft/phi-4-multimodal" "--model_path" "." "--log" "debug"
