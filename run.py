import subprocess
import time
import sys
import os

def run_server(name, command, cwd):
    print(f"Starting {name}...")
    return subprocess.Popen(command, cwd=cwd, shell=True)

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, "backend")
    frontend_dir = os.path.join(project_root, "frontend")

    # Start Backend
    backend_proc = run_server("Backend", [sys.executable, "run.py"], backend_dir)
    
    # Start Frontend
    frontend_proc = run_server("Frontend", [sys.executable, "run.py"], frontend_dir)

    print("\n" + "="*50)
    print("GraveFood System Separated")
    print(f"Frontend: http://localhost:5000")
    print(f"Backend:  http://localhost:8000")
    print("="*50 + "\n")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")
