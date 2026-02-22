import os, sys, time, subprocess, webbrowser

def get_py():
    root = os.path.dirname(os.path.abspath(__file__))
    venv = os.path.join(root, 'venv', 'Scripts' if os.name == 'nt' else 'bin', 'python' + ('.exe' if os.name == 'nt' else ''))
    return venv if os.path.exists(venv) else sys.executable

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    py, npm = get_py(), 'npm.cmd' if os.name == 'nt' else 'npm'
    
    # Sync environment
    print(">> Syncing dependencies...")
    subprocess.call([py, '-m', 'pip', 'install', '-r', os.path.join(root, 'backend', 'requirements.txt')])
    
    fr_dir = os.path.join(root, 'frontend')
    if not os.path.exists(os.path.join(fr_dir, 'node_modules')):
        subprocess.call([npm, 'install'], cwd=fr_dir)

    # Launch
    procs = [
        subprocess.Popen([py, '-m', 'uvicorn', 'app.main:app', '--reload'], cwd=os.path.join(root, 'backend')),
        subprocess.Popen([npm, 'run', 'dev'], cwd=fr_dir)
    ]

    time.sleep(2)
    webbrowser.open("http://localhost:5173")
    print(">> Factify running at http://localhost:5173 (Ctrl+C to stop)")

    try:
        while all(p.poll() is None for p in procs): time.sleep(1)
    except KeyboardInterrupt: pass
    finally:
        for p in procs: p.terminate()
        print(">> Stopped.")

if __name__ == "__main__":
    main()

