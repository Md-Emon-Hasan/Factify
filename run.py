import os
import sys
import time
import subprocess
import webbrowser

def setup(root):
    npm = 'npm.cmd' if os.name == 'nt' else 'npm'
    
    try:
        subprocess.call([npm, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Error: Node.js/NPM is not installed.")
        sys.exit(1)

    print("Checking backend dependencies...")
    req_path = os.path.join(root, 'backend', 'requirements.txt')
    if os.path.exists(req_path):
        # Remove -q to show progress if it's downloading large files like TensorFlow
        subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', req_path])
    
    print("Checking frontend setup...")
    fr_dir = os.path.join(root, 'frontend')
    if not os.path.exists(os.path.join(fr_dir, 'node_modules')):
        print("Installing frontend dependencies (this may take a few minutes)...")
        subprocess.call([npm, 'install'], cwd=fr_dir)

def main():
    root = os.path.abspath(os.path.dirname(__file__))
    setup(root)

    npm = 'npm.cmd' if os.name == 'nt' else 'npm'
    
    # Start processes
    procs = [
        subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload'], cwd=os.path.join(root, 'backend')),
        subprocess.Popen([npm, 'run', 'dev'], cwd=os.path.join(root, 'frontend'))
    ]

    print("\nFactify is starting...")
    time.sleep(3) # Give it a moment to start
    webbrowser.open("http://localhost:5173")
    print("Running at http://localhost:5173\nPress Ctrl+C to stop.")

    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            p.terminate()
        print("\nStopped.")

if __name__ == "__main__":
    main()

