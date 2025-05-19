<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        DB::table('llms')
            ->where('config', '{"react_btn":["feedback","translate","quote","other"]}')
            ->update(['config' => '{"react_btn":["feedback","quote","other"]}']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::table('llms')
            ->where('config', '{"react_btn":["feedback","quote","other"]}')
            ->update(['config' => '{"react_btn":["feedback","translate","quote","other"]}']);
    }
};
