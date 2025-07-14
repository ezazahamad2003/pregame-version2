#!/usr/bin/env python3
"""
Standalone Prospect Profile Manager

Run this script to manage your saved prospect profiles.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.profile_cli import ProfileCLI

def main():
    """Main entry point for the standalone profile manager"""
    print("🎯 PREGAME PROSPECT PROFILE MANAGER")
    print("=" * 50)
    print("Standalone tool for managing your saved prospect profiles")
    print("=" * 50)
    
    # Check if profiles directory exists
    profiles_dir = Path("profiles")
    if not profiles_dir.exists():
        print("❌ No profiles directory found.")
        print("💡 Run the main discovery tool first to create prospect profiles.")
        return
    
    # Initialize and run the CLI
    cli = ProfileCLI()
    cli.run()

if __name__ == "__main__":
    main() 