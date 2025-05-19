pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:diffusers/
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:diffusers/" "Diffusers" --image "..\..\windows\executors\painter\painter.png" --order "321000"
popd
pushd ..\..\..\src\executor\image_generation\
start /b "" "python" main.py "--access_code" ".model:diffusers/"
popd
