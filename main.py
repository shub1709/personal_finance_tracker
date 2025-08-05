#!/usr/bin/env python3
"""
Finance Tracker - Main Entry Point
Run this file to start the Streamlit application
"""

import sys
import subprocess

def main():
    """Main entry point for the application"""
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Finance Tracker stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Finance Tracker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()