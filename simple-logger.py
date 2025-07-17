import time
import datetime
import sys
import os
import pathlib

# Try to import systemd journal module for journald logging
journald_available = False
try:
    from systemd import journal
    journald_available = True
    print("Successfully imported systemd.journal module.")
except ImportError as e:
    print(f"systemd.journal module not available: {e}")
    print("Journald logging will be disabled.")

# Configuration from environment variables with defaults
try:
    DURATION_MINUTES = int(os.environ.get('DURATION_MINUTES', 20))
    if DURATION_MINUTES <= 0:
        print("Error: DURATION_MINUTES must be a positive integer")
        sys.exit(1)
except ValueError:
    print("Error: DURATION_MINUTES must be a valid integer")
    sys.exit(1)

try:
    LOGS_PER_MINUTE = int(os.environ.get('LOGS_PER_MINUTE', 2))
    if LOGS_PER_MINUTE <= 0:
        print("Error: LOGS_PER_MINUTE must be a positive integer")
        sys.exit(1)
except ValueError:
    print("Error: LOGS_PER_MINUTE must be a valid integer")
    sys.exit(1)

LOG_DIRECTORY = os.environ.get('LOG_DIRECTORY', '/tmp/logs')
SLEEP_SECONDS = 60 / LOGS_PER_MINUTE
ENABLE_JOURNALD = os.environ.get('ENABLE_JOURNALD', '').lower() in ('true', '1', 'yes') and journald_available
SYSLOG_IDENTIFIER = os.environ.get('SYSLOG_IDENTIFIER', 'simple-logger')

# Create log directory if it doesn't exist
try:
    pathlib.Path(LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
except PermissionError:
    print(f"Error: Permission denied when creating log directory '{LOG_DIRECTORY}'")
    print(f"Please ensure you have write permissions to this location or specify a different directory using LOG_DIRECTORY environment variable")
    sys.exit(1)
except OSError as e:
    print(f"Error: Failed to create log directory '{LOG_DIRECTORY}': {e}")
    print(f"Please specify a valid directory using LOG_DIRECTORY environment variable")
    sys.exit(1)

# Create a log file with timestamp in the name
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIRECTORY, f"application_log_{timestamp}.log")
try:
    log_file = open(log_file_path, "w")
except PermissionError:
    print(f"Error: Permission denied when creating log file '{log_file_path}'")
    print(f"Please ensure you have write permissions to this location or specify a different directory using LOG_DIRECTORY environment variable")
    sys.exit(1)
except OSError as e:
    print(f"Error: Failed to create log file '{log_file_path}': {e}")
    print(f"Please specify a valid directory using LOG_DIRECTORY environment variable")
    sys.exit(1)

print(f"Starting logger. Will run for {DURATION_MINUTES} minutes, logging {LOGS_PER_MINUTE} times per minute.")
print(f"Logs will be written to: {log_file_path}")
if ENABLE_JOURNALD:
    print(f"Journald logging is enabled")
print(f"Press Ctrl+C to stop.")

# Write the same information to the log file
log_file.write(f"Starting logger. Will run for {DURATION_MINUTES} minutes, logging {LOGS_PER_MINUTE} times per minute.\n")
log_file.write(f"Logs will be written to: {log_file_path}\n")
log_file.flush()

start_time = time.time()
end_time = start_time + (DURATION_MINUTES * 60)
log_count = 0

try:
    while time.time() < end_time:
        log_count += 1
        timestamp = datetime.datetime.now().isoformat()
        message = f"[{timestamp}] Log entry #{log_count}: Application is running"
        
        # Write to stdout
        print(message)
        sys.stdout.flush()  # Ensure logs are flushed immediately
        
        # Write to log file
        log_file.write(message + "\n")
        log_file.flush()
        
        # Write to journald if enabled
        if ENABLE_JOURNALD:
            try:
                log_data = {
                    "MESSAGE": f"Log entry #{log_count}: Application is running",
                    "PRIORITY": journal.LOG_INFO,
                    "SYSLOG_IDENTIFIER": SYSLOG_IDENTIFIER,
                    "TIMESTAMP": timestamp,
                    "LOG_COUNT": str(log_count)
                }
                
                journal.send(**log_data)
                print(f"Sent log #{log_count} to journald with identifier '{SYSLOG_IDENTIFIER}'")
            except Exception as e:
                print(f"Error sending to journald: {e}")
        
        # Sleep until next log interval
        time.sleep(SLEEP_SECONDS)
        
    print(f"Logger completed after {DURATION_MINUTES} minutes with {log_count} log entries.")
    log_file.write(f"Logger completed after {DURATION_MINUTES} minutes with {log_count} log entries.\n")
    
except KeyboardInterrupt:
    print(f"Logger stopped manually after {log_count} log entries.")
    log_file.write(f"Logger stopped manually after {log_count} log entries.\n")
finally:
    log_file.close()
