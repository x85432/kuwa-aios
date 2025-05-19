<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Hash;
use App\Models\User;
use App\Models\Permissions;
use App\Models\GroupPermissions;
use App\Models\Groups;
use DB;

class CreateAdminUser extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'create:admin-user
                            {--name= : The admin username}
                            {--email= : The admin email}
                            {--password= : The admin password}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Create an admin user and assign permissions to the admin group';

    /**
     * Execute the console command.
     *
     * @return void
     */
    public function handle()
    {
        try {
            DB::beginTransaction(); // Start a database transaction

            // If options are not passed, prompt for them
            $name = $this->option('name') ?: $this->ask('Enter admin username');
            $email = $this->option('email') ?: $this->ask('Enter admin email');
            $password = $this->option('password') ?: $this->secret('Enter admin password');

            // Check if any of the required options are missing, and prompt if needed
            if (!$name || !$email || !$password) {
                $this->error('All options (name, email, and password) must be provided either via options or prompts.');
                return;
            }

            // Create a new admin user
            $admin_group = Groups::firstOrCreate(['name' => 'Admins'], ['describe' => 'Default seeded Admin group']);
            $admin_user = new User();
            $admin_user->fill([
                'name' => $name,
                'email' => $email,
                'email_verified_at' => now(),
                'password' => Hash::make($password),
                'group_id' => $admin_group->id,
            ]);
            $admin_user->save();

            // Clear and Give all permissions to the migrated admin group
            GroupPermissions::where('group_id', '=', $admin_group->id)->delete();
            $perm_records = [];
            $currentTimestamp = now();
            foreach (Permissions::get() as $perm) {
                $perm_records[] = [
                    'group_id' => $admin_group->id,
                    'perm_id' => $perm->id,
                    'created_at' => $currentTimestamp,
                    'updated_at' => $currentTimestamp,
                ];
            }
            GroupPermissions::insert($perm_records);

            DB::commit();

            // Success message
            $this->info('Admin user created and permissions assigned successfully.');
        } catch (\Exception $e) {
            DB::rollBack(); // Rollback the transaction in case of an exception
            $this->error('Failed to create admin user: ' . $e->getMessage());
        }
    }
}
