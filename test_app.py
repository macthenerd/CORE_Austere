#!/usr/bin/env python3
"""
Test runner for CORE_Austere - creates test DB and starts the app
"""
import os
import subprocess
import sys

def main():
    print("CORE_Austere Test Runner")
    print("=" * 40)
    
    # Step 1: Create test database
    print("1. Creating test database...")
    result = subprocess.run([sys.executable, "create_test_db.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] Failed to create test database:")
        print(result.stderr)
        return
    print(result.stdout)
    
    # Step 2: Start the app
    db_path = "test_reports.db"
    if not os.path.exists(db_path):
        print(f"[ERROR] Test database not found: {db_path}")
        return
        
    print("2. Starting CORE_Austere backend...")
    print(f"   Database: {db_path}")
    print("   Server: http://127.0.0.1:8000")
    print("   Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "run_app.py", "--db", db_path])
    except KeyboardInterrupt:
        print("\nCORE_Austere stopped")

if __name__ == "__main__":
    main()
