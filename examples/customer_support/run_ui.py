#!/usr/bin/env python3
"""
Launch script for the Customer Support DAPERL Dashboard.

This script starts both the FastAPI backend and React frontend.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path
import signal
import time
import select
import threading


def print_banner():
    """Print a nice banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     Customer Support DAPERL Dashboard                     ║
    ║     Intelligent Support Automation Monitoring             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import temporalio
        print("  ✓ Python dependencies installed")
    except ImportError as e:
        print(f"  ✗ Missing Python dependency: {e}")
        print("\n  Install with: cd examples/customer_support && poetry install")
        return False
    
    # Check if npm is available
    if subprocess.run(["which", "npm"], capture_output=True).returncode != 0:
        print("  ✗ npm not found")
        print("  Please install Node.js and npm")
        return False
    print("  ✓ npm found")
    
    # Check if frontend dependencies are installed
    frontend_dir = Path(__file__).parent / "ui" / "frontend"
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("  ✗ Frontend dependencies not installed")
        print(f"\n  Install with: cd {frontend_dir} && npm install")
        return False
    print("  ✓ Frontend dependencies installed")
    
    return True


def start_backend():
    """Start the FastAPI backend server."""
    print("\n🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "ui" / "backend"
    
    # Change to backend directory and start uvicorn
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)  # Add project root to path
    
    backend_process = subprocess.Popen(
        ["python", "main.py"],
        cwd=backend_dir,
        env=env
    )
    
    # Wait a bit and check if it started successfully
    time.sleep(2)
    if backend_process.poll() is not None:
        print("  ✗ Backend failed to start")
        return None
    
    print("  ✓ Backend running on http://localhost:8000")
    return backend_process


def start_frontend():
    """Start the React frontend dev server."""
    print("\n🚀 Starting frontend server...")
    frontend_dir = Path(__file__).parent / "ui" / "frontend"
    
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )
    
    # Wait a bit and check if it started successfully
    time.sleep(3)
    if frontend_process.poll() is not None:
        print("  ✗ Frontend failed to start")
        return None
    
    print("  ✓ Frontend running on http://localhost:5173")
    return frontend_process


def main():
    """Main entry point."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend server")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Dashboard is running!")
    print("="*60)
    print("\n📍 URLs:")
    print("  Frontend: http://localhost:5173")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    
    print("\n💡 Next Steps:")
    print("  1. Make sure Temporal server is running: temporal server start-dev")
    print("  2. Make sure worker is running: poetry run python scripts/run_worker.py")
    print("  3. Start a workflow: poetry run python examples/customer_support/run_example.py")
    print("  4. Open http://localhost:5173 in your browser")
    
    print("\n🎮 Controls:")
    print("  Press 'b' + Enter to restart backend")
    print("  Press 'f' + Enter to restart frontend")
    print("  Press 'q' + Enter or Ctrl+C to quit")
    print("="*60)
    print()
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✓ Servers stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Input handling thread
    input_command = {"value": None}
    
    def read_input():
        while True:
            try:
                cmd = input().strip().lower()
                if cmd in ['b', 'f', 'q']:
                    input_command["value"] = cmd
            except:
                break
    
    input_thread = threading.Thread(target=read_input, daemon=True)
    input_thread.start()
    
    # Keep the script running and monitor processes
    try:
        while True:
            # Check for input commands
            if input_command["value"]:
                cmd = input_command["value"]
                input_command["value"] = None
                
                if cmd == 'q':
                    signal_handler(None, None)
                elif cmd == 'b':
                    print("\n🔄 Restarting backend...")
                    backend_process.terminate()
                    backend_process.wait()
                    backend_process = start_backend()
                    if not backend_process:
                        print("\n❌ Failed to restart backend server")
                        frontend_process.terminate()
                        sys.exit(1)
                elif cmd == 'f':
                    print("\n🔄 Restarting frontend...")
                    frontend_process.terminate()
                    frontend_process.wait()
                    frontend_process = start_frontend()
                    if not frontend_process:
                        print("\n❌ Failed to restart frontend server")
                        backend_process.terminate()
                        sys.exit(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n⚠️  Backend process died unexpectedly")
                frontend_process.terminate()
                sys.exit(1)
            
            if frontend_process.poll() is not None:
                print("\n⚠️  Frontend process died unexpectedly")
                backend_process.terminate()
                sys.exit(1)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
