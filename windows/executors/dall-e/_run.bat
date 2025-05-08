pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:openai/dall-e
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:openai/dall-e" "DALL-E" --order=421000 --image "..\..\windows\executors\dall-e\dall-e.png"
popd
pushd ..\..\..\src\executor\image_generation
start /b "" "python" dall_e.py "--access_code" ".model:openai/dall-e"
popd
