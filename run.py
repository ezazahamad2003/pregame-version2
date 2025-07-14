#!/usr/bin/env python3
"""
Pregame Web Application Launcher

This script starts the Pregame web application from the reorganized folder structure.
"""

import os
import sys
import subprocess

def main():
    # Change to the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Change to backend directory and run the web app
    os.chdir(backend_dir)
    
    print("🚀 Starting Pregame Web Application...")
    print("📁 Running from backend directory...")
    
    try:
        # Run the web application
        subprocess.run([sys.executable, 'web_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Application failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == '__main__':
    main() 