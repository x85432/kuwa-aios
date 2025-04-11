pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/uploader
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/uploader" "Uploader" --image "..\..\windows\executors\uploader\upload.png" --order "999020"
popd
pushd ..\..\..\src\executor\uploader
start /b "" "python" main.py "--access_code" ".tool/kuwa/uploader"
popd
