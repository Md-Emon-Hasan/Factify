import os
import sys
import time
import subprocess
import webbrowser

def get_python_exe():
    """Get the path to the python executable within the venv."""
    is_windows = os.name == 'nt'
    venv_bin = 'Scripts' if is_windows else 'bin'
    python_exe = 'python.exe' if is_windows else 'python'
    return os.path.join(os.getcwd(), 'venv', venv_bin, python_exe)

def start_services():
    root = os.getcwd()
    venv_dir = os.path.join(root, 'venv')
    python_path = get_python_exe()
    npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
    
    # Init virtual environment if missing
    if not os.path.exists(venv_dir):
        print(">> Setting up virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Update dependencies
    print(">> Syncing backend dependencies...")
    subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([python_path, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
    
    print(">> Syncing frontend dependencies...")
    frontend_dir = os.path.join(root, 'frontend')
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        subprocess.run([npm_cmd, 'install'], cwd=frontend_dir, check=True)

    # Boot up servers
    print(">> Launching Factify...")
    backend_proc = subprocess.Popen(
        [python_path, '-m', 'uvicorn', 'app.main:app', '--reload'], 
        cwd=os.path.join(root, 'backend')
    )
    frontend_proc = subprocess.Popen(
        [npm_cmd, 'run', 'dev'], 
        cwd=frontend_dir
    )

    time.sleep(3)
    
    banner = f"""
{'='*50}
Factify is now live!
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
{'='*50}
"""
    print(banner)
    webbrowser.open("http://localhost:5173")

    try:
        while True:
            if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n>> Shutting down...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        print(">> All services stopped.")

if __name__ == "__main__":
    start_services()

