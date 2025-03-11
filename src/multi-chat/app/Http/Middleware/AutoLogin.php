<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Illuminate\Support\Facades\App;
use Illuminate\Support\Facades\Cookie;

class AutoLogin
{
    /**
     * Auto login if configured in .env
     * Require both APP_AUTO_ACC and APP_AUTO_PASS to be filled in.
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Check if the user is already logged in
        if (!\Auth::check()) {
            $email = config('app.APP_AUTO_EMAIL');
            if ($email) {
                $user = \App\Models\User::where('email', $email)->first();
                if ($user) {
                    \Auth::login($user);
                }
            }
        }
        
        return $next($request);
    }
    
}
