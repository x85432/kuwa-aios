cd ../..

call composer install --no-dev --optimize-autoloader --no-interaction --ansi

call php artisan key:generate --ansi
call php artisan db:seed --class=InitSeeder --force --ansi
call php artisan migrate --force --ansi

rmdir /Q /S public\storage
rmdir /Q /S storage\app\public\root\custom
rmdir /Q /S storage\app\public\root\database
rmdir /Q /S storage\app\public\root\bin
rmdir /Q /S storage\app\public\root\bot

call php artisan storage:link --ansi

call npm audit fix --loglevel verbose --force
call npm install --color=always
call npm audit fix --loglevel verbose --force
call npm ci --no-audit --no-progress --color=always

call php artisan route:cache --ansi
call php artisan view:cache --ansi
call php artisan optimize --ansi

call npm run build --color=always

call php artisan config:cache --ansi
