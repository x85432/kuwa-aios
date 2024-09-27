<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use App\Models\LLMs;
use App\Models\Permissions;
use App\Models\GroupPermissions;

return new class extends Migration
{
    private $access_code = "redirector";
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        $model = new LLMs;
        $model->fill([
            'name' => 'Redirector',
            'access_code' => $this->access_code,
            'image' => '../images/redirector.png',
            'order' => 99999,
            'enabled' => 1,
            'description' => 'A built-in dummy executor to seamlessly redirect users to external web applications.'
        ]);
        $model->save();
        $perm = new Permissions;
        $perm->fill(["name" => "model_" . $model->id]);
        $perm->save();

        $currentTimestamp = now();
        $targetPermID = Permissions::where('name', '=', 'tab_Manage')->first()->id;
        $groups = GroupPermissions::pluck('group_id')->toArray();

        foreach ($groups as $group) {
            GroupPermissions::where('group_id', $group)
                ->where('perm_id', '=', $perm->id)
                ->delete();
            if (GroupPermissions::where('group_id', $group)->where('perm_id', '=', $targetPermID)->exists()) {
                GroupPermissions::insert([
                    'group_id' => $group,
                    'perm_id' => $perm->id,
                    'created_at' => $currentTimestamp,
                    'updated_at' => $currentTimestamp,
                ]);
            }
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        LLMs::where("name", "=", $this->access_code)->delete();
    }
};
