<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUniqueUntilProcessing;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Bus\Queueable;
use App\Models\SystemSetting;
use App\Jobs\RequestChat;
use App\Models\LLMs; 
use Illuminate\Support\Collection;
use App\Jobs\Middleware\HealthRateLimit;

class HealthCheck implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * The number of seconds after which the job's unique lock will be released.
     *
     * @var int
     */
    public $uniqueFor = 5;

    /**
     * Get the unique ID for the job.
     */
    public function uniqueId(): string
    {
        return 'health_check_job';
    }

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {
        // Fetch the 'agent_location' value from the SystemSetting model
        $systemSetting = SystemSetting::where('key', 'agent_location')->first();
    
        if ($systemSetting && $systemSetting->value) {
            // Send GET request to the endpoint
            $response = Http::get($systemSetting->value . '/' . RequestChat::$agent_version . '/worker/debug');
    
            if ($response->ok()) {
                // Get the response body and all LLMs
                $responseData = $response->body();
                $llms = LLMs::select('id', 'access_code')->get();
    
                // Separate found and not found LLMs
                $foundIds = [];
                foreach ($llms as $llm) {
                    if (strpos($responseData, $llm->access_code) !== false) {
                        $foundIds[] = $llm->id;
                    }
                }
    
                // Update healthy status and log results in one query each
                LLMs::whereIn('id', $foundIds)->update(['healthy' => true]);
                LLMs::whereNotIn('id', $foundIds)->update(['healthy' => false]);
    
                Log::info('LLM health status updated.', [
                    'found' => $foundIds,
                    'not_found' => array_diff($llms->pluck('id')->toArray(), $foundIds),
                ]);
            } else {
                Log::error('GET request failed:', ['status' => $response->status()]);
            }
        } else {
            Log::error('No valid endpoint found for agent_location');
        }
    }
    
    /**
     * Get the middleware the job should pass through.
     *
     * @return array<int, object>
     */
    public function middleware(): array
    {
        return [new HealthRateLimit()];
    }
}
