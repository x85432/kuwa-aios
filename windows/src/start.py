import os, subprocess, shutil, requests, time, sys, re, psutil, concurrent.futures, threading

processes = []
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
kuwa_root = os.getenv("KUWA_ROOT", os.path.join(base_dir, "kuwa_root"))
os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
log_path = os.path.join(base_dir, "logs", "start.log")
if os.path.exists(log_path):
    os.remove(log_path)

log_lock = threading.Lock()

class Logger:
    def __init__(self, stream, path):
        self.stream, self.path = stream, path
        self.lock = threading.Lock()
    def write(self, msg):
        self.stream.write(msg); self.stream.flush()
        with self.lock:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(msg); f.flush()
    def flush(self): self.stream.flush()

sys.stdout = Logger(sys.stdout, log_path)
sys.stderr = Logger(sys.stderr, log_path)

def logged_input(prompt=""):
    if prompt: print(prompt, end='', flush=True)
    line = sys.__stdin__.readline()
    if line == '': raise EOFError
    print(line.rstrip('\n'))
    return line.rstrip('\n')
input = logged_input

def run_background(cmd, cwd=None):
    print(f"Starting: {cmd}")
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=1, universal_newlines=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    processes.append(proc)
    def log_output():
        with open(log_path, 'a', encoding='utf-8') as f:
            for line in proc.stdout:
                print(line, end='')
                with log_lock:
                    f.write(line); f.flush()
    threading.Thread(target=log_output, daemon=True).start()
    return proc

def terminate_proc(proc, current_pid):
    try:
        if proc.info['pid'] == current_pid: return
        if proc.info.get('exe', '').startswith(os.path.abspath(base_dir, '..')):
            print(f"Terminating process {proc.pid}: {proc.info['exe']}")
            proc.terminate()
            try: proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                print(f"Force killing {proc.pid}")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied): pass

def hard_exit(restart):
    services = [
        ("Nginx", r'.\nginx.exe -s quit', os.path.join(base_dir, "packages", os.environ.get("nginx_folder") or "nginx")),
        ("Redis", "redis-cli.exe shutdown", os.path.join(base_dir, "packages", os.environ.get("redis_folder") or "redis")),
        ("Laravel worker", "php artisan worker:stop", os.path.abspath("../src/multi-chat"))
    ]

    for name, cmd, cwd in services:
        try:
            subprocess.call(cmd, cwd=cwd, shell=True)
            print(f"{name} shutdown issued.")
        except Exception as e:
            print(f"Failed to stop {name}: {e}")
            
    current_pid = os.getpid()
    current_proc = None
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(terminate_proc, p, current_pid) for p in psutil.process_iter(['pid','exe']) if p.pid != current_pid or (current_proc:=p)]
        concurrent.futures.wait(futures)
    if restart:
        subprocess.Popen(["start.bat"], shell=True)
    time.sleep(5)
    if current_proc:
        print(f"Terminating current Python process (PID {current_pid}) last.")
        current_proc.terminate()
    os._exit(0)

def extract_packages():
    zip_path = os.path.abspath("../scripts/windows-setup-files/package.zip")
    if os.path.exists(zip_path):
        print("Extracting packages...")
        subprocess.call("build.bat restore", shell=True, cwd=os.path.abspath("../scripts/windows-setup-files"))
        print("Unzipping successful.")
        for f in ["bin", "database", "custom", "bootstrap/bot"]:
            os.makedirs(os.path.join(kuwa_root, f), exist_ok=True)
        shutil.copytree("../src/bot/init", os.path.join(kuwa_root, "bootstrap/bot"), dirs_exist_ok=True)
        shutil.copytree("../src/tools", os.path.join(kuwa_root, "bin"), dirs_exist_ok=True)
        shutil.rmtree(os.path.join(kuwa_root, "bin", "test"), ignore_errors=True)
        print("Filesystem initialized.")
        prepare_laravel()

def prepare_laravel():
    multi_chat = os.path.abspath("../src/multi-chat")
    env_file = os.path.join(multi_chat, ".env")
    if not os.path.exists(env_file):
        shutil.copyfile(os.path.join(multi_chat, ".env.dev"), env_file)
    for cmd in [
        "php artisan key:generate --force",
        "php artisan db:seed --class=InitSeeder --force",
        "php artisan migrate --force",
        "php artisan storage:link",
        "php ../../windows/packages/composer.phar dump-autoload --optimize",
        "php artisan route:cache",
        "php artisan view:cache",
        "php artisan optimize",
        "npm.cmd run build",
        "php artisan config:cache",
        "php artisan config:clear"]:
        subprocess.call(cmd, cwd=multi_chat, shell=True)

def extract_executor_access_code(path):
    with open(path) as f:
        for line in f:
            if line.lower().startswith('set '):
                m = re.match(r'set\s+EXECUTOR_ACCESS_CODE\s*=\s*(.*)', line, re.I)
                if m: return m.group(1).strip()
    return None

def start_servers():
    redis_path = os.path.join(base_dir, "packages", os.environ.get("redis_folder", "redis"))
    rdb = os.path.join(redis_path, "dump.rdb")
    if os.path.exists(rdb): os.remove(rdb)
    run_background("redis-server.exe redis.conf", cwd=redis_path)

    web_path = os.path.abspath("../src/multi-chat")
    subprocess.call('php artisan web:config --settings="updateweb_path=%PATH%"', cwd=web_path, shell=True)
    run_background("php artisan worker:start 10", cwd=web_path)

    kernel_path = os.path.abspath("../src/kernel")
    try: os.remove(os.path.join(kernel_path, "records.pickle"))
    except FileNotFoundError: pass
    run_background("kuwa-kernel", cwd=kernel_path)

    while True:
        try: requests.get("http://127.0.0.1:9000", timeout=1); break
        except: time.sleep(1)

    exclude_args = []
    executors_dir = os.path.join(base_dir, "executors")
    for folder in os.listdir(executors_dir):
        folder_path = os.path.join(executors_dir, folder)
        if os.path.isdir(folder_path):
            run_bat, init_bat = os.path.join(folder_path, "run.bat"), os.path.join(folder_path, "init.bat")
            if os.path.exists(init_bat) and not os.path.exists(run_bat):
                subprocess.call("init.bat quick", cwd=folder_path, shell=True)
            if os.path.exists(run_bat):
                subprocess.call("run.bat", cwd=folder_path, shell=True)
                code = extract_executor_access_code(run_bat)
                if code: exclude_args.append(f"--exclude={code}")

    if exclude_args:
        subprocess.call(f"php artisan model:prune --force {' '.join(exclude_args)}", cwd=web_path, shell=True)

    php_path = os.path.join(base_dir, "packages", os.environ.get("php_folder", "php"))
    run_background("php-cgi.exe -b 127.0.0.1:9123", cwd=php_path)

    nginx_folder = os.environ.get("nginx_folder", "nginx")
    nginx_html = os.path.join(base_dir, "packages", nginx_folder, "html")
    if os.path.exists(nginx_html):
        try: os.unlink(nginx_html)
        except OSError: shutil.rmtree(nginx_html, ignore_errors=True)
    subprocess.run(f'mklink /j "{nginx_html}" "{os.path.abspath("../src/multi-chat/public")}"', shell=True, check=True)

    run_background("nginx.exe", cwd=os.path.join(base_dir, "packages", nginx_folder))
    print("Nginx started!")

    subprocess.call("php artisan model:reset-health", cwd=web_path, shell=True)
    time.sleep(4)
    subprocess.call("src\\import_bots.bat", shell=True)
    time.sleep(1)

    print("System initialized. Press Ctrl+C or type 'stop' to exit.")
    subprocess.call('start http://127.0.0.1', shell=True)

def command_loop():
    while True:
        try:
            cmd = input("Enter a command (stop, seed, hf login, reload): ").strip().lower()
            if cmd == "stop": hard_exit(False)
            elif cmd == "seed":
                print("Running seed command...")
                seed_path = os.path.abspath("../src/multi-chat/executables/bat")
                subprocess.call("AdminSeeder.bat", cwd=seed_path, shell=True)
            elif cmd == "hf login":
                print("Running HuggingFace login...")
                subprocess.call("huggingface-cli.exe login", shell=True)
            elif cmd == "reload":
                print("Restarting script...")
                hard_exit(True)
            else:
                print("Unknown command.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            hard_exit(False)

if __name__ == "__main__":
    extract_packages()
    start_servers()
    command_loop()
