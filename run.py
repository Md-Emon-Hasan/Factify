import os, sys, time, subprocess, webbrowser

def get_py():
    is_win = os.name == 'nt'
    bin = 'Scripts' if is_win else 'bin'
    exe = 'python.exe' if is_win else 'python'
    return os.path.join(os.getcwd(), 'venv', bin, exe)

def start():
    root = os.getcwd()
    py = get_py()
    npm = 'npm.cmd' if os.name == 'nt' else 'npm'
    
    if not os.path.exists('venv'):
        print("Setting up venv...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    print("Updating backend...")
    subprocess.run([py, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
    
    print("Updating frontend...")
    if not os.path.exists('frontend/node_modules'):
        subprocess.run([npm, 'install'], cwd='frontend', check=True)

    print("Launching servers...")
    b_proc = subprocess.Popen([py, '-m', 'uvicorn', 'app.main:app', '--reload'], cwd='backend')
    f_proc = subprocess.Popen([npm, 'run', 'dev'], cwd='frontend')

    time.sleep(3)
    print("\nFactify is ready!")
    print("Frontend: http://localhost:5173")
    print("Backend: http://localhost:8000\n")
    webbrowser.open("http://localhost:5173")

    try:
        while b_proc.poll() is None and f_proc.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        b_proc.terminate()
        f_proc.terminate()

if __name__ == "__main__":
    start()
