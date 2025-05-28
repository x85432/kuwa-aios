pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn/qualcomm/stable-diffusion
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn/qualcomm/stable-diffusion" "Painter @NPU" --order=120001 --image "..\..\windows\executors\qnn-stable-diffusion\sd_qnn.png"
popd
pushd ..\..\..\src\executor\image_generation
start /b "" "python" .\qnn_stable_diffusion.py "--access_code" ".model:qnn/qualcomm/stable-diffusion" "--model" "qualcomm/Stable-Diffusion-v1.5" "--qnn_binaries" "..\..\..\windows\packages\qnn-binaries" --log debug
popd