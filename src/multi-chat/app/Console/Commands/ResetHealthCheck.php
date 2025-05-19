<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\LLMs;

class ResetHealthCheck extends Command
{
    /**
     * The name and signature of the console command.
     *
     * Run it with: php artisan llms:update-healthy
     */
    protected $signature = 'model:reset-health';

    /**
     * The console command description.
     */
    protected $description = 'Reset all model health status';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        LLMs::query()->update(['healthy' => now()]);

        $this->info("Reset all model health status");
    }
}
