#!/usr/bin/env python3
"""
Simple auto-updater that runs the Django management command periodically
This can run independently without Django framework loaded
"""

import subprocess
import time
import sys
import os
from datetime import datetime

# Configuration
BACKEND_DIR = "/home/nguyentukien/Documents/web-track-naver-vietnam-ai-hackathon-NguyenTuKien/Backend"
VENV_PYTHON = "/home/nguyentukien/Documents/web-track-naver-vietnam-ai-hackathon-NguyenTuKien/Backend/.venv/bin/python"
INTERVAL = 60  # seconds (1 minute)
LOG_FILE = os.path.join(BACKEND_DIR, "logs", "auto_updater.log")

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Print to console
    print(log_entry.strip())
    
    # Write to log file
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def run_update():
    """Run the Django update_status command"""
    try:
        # Change to backend directory
        os.chdir(BACKEND_DIR)
        
        # Try different Python executables
        python_executables = [
            VENV_PYTHON,
            "/bin/python3.10",
            "python3",
            "python"
        ]
        
        for python_exec in python_executables:
            try:
                # Check if python executable exists
                if python_exec.startswith("/") and not os.path.exists(python_exec):
                    continue
                    
                cmd = [python_exec, "manage.py", "update_status"]
                log_message(f"Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    log_message(f"SUCCESS: {result.stdout.strip()}")
                    return True
                else:
                    log_message(f"ERROR (code {result.returncode}): {result.stderr.strip()}")
                    
            except FileNotFoundError:
                log_message(f"Python executable not found: {python_exec}")
                continue
            except subprocess.TimeoutExpired:
                log_message("ERROR: Command timed out")
                continue
            except Exception as e:
                log_message(f"ERROR with {python_exec}: {str(e)}")
                continue
        
        log_message("ERROR: All Python executables failed")
        return False
        
    except Exception as e:
        log_message(f"CRITICAL ERROR: {str(e)}")
        return False

def main():
    """Main scheduler loop"""
    log_message("Starting Django Auto Status Updater")
    log_message(f"Backend directory: {BACKEND_DIR}")
    log_message(f"Update interval: {INTERVAL} seconds")
    log_message(f"Log file: {LOG_FILE}")
    
    try:
        while True:
            log_message("Running scheduled status update...")
            success = run_update()
            
            if success:
                log_message("Status update completed successfully")
            else:
                log_message("Status update failed")
            
            log_message(f"Waiting {INTERVAL} seconds until next update...")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        log_message("Scheduler stopped by user (Ctrl+C)")
    except Exception as e:
        log_message(f"Scheduler crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
