pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model/taide/taide-lx
pushd ..\..\..\src\multi-chat
php artisan model:config ".model/taide/taide-lx" "🇹🇼 TAIDE LX-8B" --image "..\..\windows\executors\taide\TAIDE.png" --order "100001"
popd
start /b "" "kuwa-executor" "llamacpp" "--access_code" ".model/taide/taide-lx" "--ngl" "-1" "--model_path" "Llama-3.1-TAIDE-LX-8B-Chat-Q4_K_M.gguf" "--system_prompt" "你是一個來自台灣的AI助理，你的名字是 TAIDE，樂於以台灣人的立場幫助使用者，會用繁體中文回答問題。"
