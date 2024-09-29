<?php

namespace App\Jobs\Middleware;

use Closure;
use Illuminate\Support\Facades\Redis;

class HealthRateLimit
{
    /**
     * Process the queued job.
     *
     * @param  \Closure(object): void  $next
     */
    public function handle(object $job, Closure $next): void
    {
        Redis::throttle('health_check')
            ->block(0)
            ->allow(1)
            ->every(5)
            ->then(
                function () use ($job, $next) {
                    $next($job);
                },
                function () use ($job) {
                    $job->delete();
                },
            );
    }
}
