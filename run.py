import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.join(root_dir, 'backend')
    frontend_dir = os.path.join(root_dir, 'frontend')

    print(f"Root Directory: {root_dir}")
    
    # Start Backend
    print("Starting Backend...")
    # Run uvicorn directly
    # Using 'uvicorn' module call
    # We run it from 'backend' directory so 'app.main' is importable
    backend_cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)

    # Start Frontend
    print("Starting Frontend...")
    # 'npm.cmd' for Windows, 'npm' for others
    npm_exec = 'npm.cmd' if os.name == 'nt' else 'npm'
    frontend_cmd = [npm_exec, 'run', 'dev']
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

    print("\n---------------------------------------------------")
    print("Factify is running!")
    print("Backend: http://localhost:8000 (usually)")
    print("Frontend: http://localhost:5173 (usually)")
    print("Press Ctrl+C to stop both services.")
    print("---------------------------------------------------\n")

    try:
        while True:
            time.sleep(0.5)
            # Check if processes have exited
            if backend_proc.poll() is not None:
                print(f"Backend process exited with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"Frontend process exited with code {frontend_proc.returncode}")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Terminate processes
        if backend_proc.poll() is None:
            backend_proc.terminate()
        if frontend_proc.poll() is None:
            frontend_proc.terminate()
        
        # Wait for them to actually exit
        backend_proc.wait()
        frontend_proc.wait()
        print("Services stopped.")

if __name__ == '__main__':
    main()
