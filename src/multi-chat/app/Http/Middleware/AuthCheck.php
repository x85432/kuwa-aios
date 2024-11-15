<?php

namespace App\Http\Middleware;
use Symfony\Component\HttpFoundation\Response;
use App\Http\Controllers\WorkerController;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\App;
use Illuminate\Http\Request;
use App\Jobs\CheckUpdate;
use App\Jobs\HealthCheck;
use Illuminate\Support\Facades\Redis;
use Closure;

class AuthCheck
{
    /**
     * Redirect user if they're required to change password
     */
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->user()->tokens()->where('name', 'API_Token')->count() != 1) {
            $request->user()->tokens()->where('name', 'API_Token')->delete();
            $request->user()->createToken('API_Token', ['access_api']);
        }
        $user_dir = 'root/homes' . '/' . auth()->id();
        if (!Storage::disk('public')->exists($user_dir)) {
            Storage::disk('public')->makeDirectory($user_dir);
        }

        if ($request->user()) {
            $jobs = Redis::lrange('queues:default', 0, -1);
            $runningJobs = [];

            foreach ($jobs as $job) {
                $jobData = json_decode($job);
                $displayName = $jobData->displayName;

                if (!in_array($displayName, $runningJobs)) {
                    $runningJobs[] = $displayName;
                } elseif (in_array($displayName, ['App\Jobs\CheckUpdate', 'App\Jobs\HealthCheck'])) {
                    Redis::lrem('queues:default', 0, $job);
                }
            }

            if ($request->user()->require_change_password) {
                return redirect()->route('change_password');
            }
        }

        Redis::throttle('health_check')->block(0)->allow(1)->every(5)->then(fn() => HealthCheck::dispatch(), fn() => null);

        return $next($request);
    }
}
