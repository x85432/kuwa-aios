set EXECUTOR_ACCESS_CODE=.tool/kuwa/copycat
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/copycat" "CopyCat" --image "..\..\windows\executors\copycat\copycat.png" --order "999000"
popd
start /b "" "kuwa-executor" "debug" "--access_code" ".tool/kuwa/copycat"