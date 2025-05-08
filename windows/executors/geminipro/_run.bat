pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:google/gemini
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:google/gemini" "Gemini" --image "..\..\windows\executors\geminipro\geminipro.png" --order "401000"
popd
start /b "" "kuwa-executor" "geminipro" "--access_code" ".model:google/gemini"
