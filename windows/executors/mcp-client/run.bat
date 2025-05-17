pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool.mcp
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool.mcp" "MCP Client" --order 999030 --image "..\..\windows\executors\mcp-client\mcp.png"
popd
pushd ..\..\..\src\executor\mcp\client
start /b "" "python" mcp-client.py "--access_code" ".tool.mcp" "--mcp_server_cmd" "python" "--mcp_server_args" "-m mcp_server_time --local-timezone=Asia/Taipei" --log debug
popd