<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use App\Models\LLMs;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        LLMs::where('name', 'Redirector')->update(['name' => 'Weblet']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        LLMs::where('name', 'Weblet')->update(['name' => 'Redirector']);
    }
};
