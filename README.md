# Simple Logger

A Python utility for generating log entries at a configurable rate. Logs are written to stdout, a log file, and optionally to systemd's journald.

## Requirements

- Python 3
- systemd-python (for journald support)
  - On Amazon Linux 2023: `systemd-devel` package
  - On Amazon Linux 2: `systemd-devel` package

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/simple-logger.git
cd simple-logger
```

2. Set up a Python virtual environment:
```
# Create a virtual environment
python3 -m venv venv  # Use python3 explicitly on Linux/macOS
# On Windows, you might use just 'python -m venv venv'

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. If using journald logging, install the required system packages first:

For Amazon Linux 2023:
```
sudo dnf install systemd-devel
```

For Amazon Linux 2:
```
sudo yum install systemd-devel
```

4. Install required Python packages:
```
pip install -r requirements.txt
```

## Usage

Run the script with Python:

```
python simple-logger.py
```

The logger will run for the configured duration, generating log entries at the specified rate.

### Error Handling

The script includes error handling for common issues:

1. **Invalid Environment Variables**:
   - If DURATION_MINUTES is not a valid integer:
     ```
     Error: DURATION_MINUTES must be a valid integer
     ```
   - If DURATION_MINUTES is zero or negative:
     ```
     Error: DURATION_MINUTES must be a positive integer
     ```
   - If LOGS_PER_MINUTE is not a valid integer:
     ```
     Error: LOGS_PER_MINUTE must be a valid integer
     ```
   - If LOGS_PER_MINUTE is zero or negative:
     ```
     Error: LOGS_PER_MINUTE must be a positive integer
     ```

2. **Log Directory Creation Failure**:
   - If the script cannot create the log directory due to permission issues:
     ```
     Error: Permission denied when creating log directory '/tmp/logs'
     Please ensure you have write permissions to this location or specify a different directory using LOG_DIRECTORY environment variable
     ```
   - If the directory creation fails for other reasons:
     ```
     Error: Failed to create log directory '/tmp/logs': [specific error message]
     Please specify a valid directory using LOG_DIRECTORY environment variable
     ```

3. **Log File Creation Failure**:
   - If the script cannot create the log file due to permission issues:
     ```
     Error: Permission denied when creating log file '/tmp/logs/application_log_20250718_123456.log'
     Please ensure you have write permissions to this location or specify a different directory using LOG_DIRECTORY environment variable
     ```
   - If the file creation fails for other reasons:
     ```
     Error: Failed to create log file '/tmp/logs/application_log_20250718_123456.log': [specific error message]
     Please specify a valid directory using LOG_DIRECTORY environment variable
     ```

In case of any errors, the script will exit with a non-zero status code (1).

## Configuration

The script can be configured using the following environment variables:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DURATION_MINUTES` | How long the logger should run (in minutes) | 20 |
| `LOGS_PER_MINUTE` | Number of log entries to generate per minute | 2 |
| `LOG_DIRECTORY` | Directory where log files will be stored | `/tmp/logs` |
| `ENABLE_JOURNALD` | Enable logging to systemd's journald (requires systemd-python, systemd-devel package) | `false` |
| `SYSLOG_IDENTIFIER` | Identifier used for journald logs (used for filtering in journalctl) | `simple-logger` |

**Note:** Journald logging will be automatically disabled if the systemd.journal module is not available (e.g., on Windows or if the required packages are not installed). The script will display a message like `systemd.journal module not available: No module named 'systemd'` at startup if journald is not available.

### Examples

Run for 10 minutes with 6 logs per minute:
```
DURATION_MINUTES=10 LOGS_PER_MINUTE=6 python simple-logger.py
```

Store logs in a custom directory:
```
LOG_DIRECTORY=./my_logs python simple-logger.py
```

Enable journald logging:
```
ENABLE_JOURNALD=true python simple-logger.py
```

Enable journald logging with a custom identifier:
```
ENABLE_JOURNALD=true SYSLOG_IDENTIFIER=my-application python simple-logger.py
```

Run with multiple custom settings:
```
DURATION_MINUTES=5 LOGS_PER_MINUTE=12 LOG_DIRECTORY=./app_logs ENABLE_JOURNALD=true SYSLOG_IDENTIFIER=app-metrics python simple-logger.py
```

## Log Output

Logs are written to:
1. Standard output (console)
2. A timestamped log file in the configured log directory
3. Systemd's journald (if enabled)

Each log entry includes a timestamp and sequential log number.

### Sample Output

Here's an example of running the logger for 2 minutes with 5 logs per minute:

```
$ DURATION_MINUTES=2 LOGS_PER_MINUTE=5 LOG_DIRECTORY=./logs python simple-logger.py
Starting logger. Will run for 2 minutes, logging 5 times per minute.
Logs will be written to: ./logs/application_log_20250717_143022.log
Press Ctrl+C to stop.
[2025-07-17T14:30:22.123456] Log entry #1: Application is running
[2025-07-17T14:30:34.234567] Log entry #2: Application is running
[2025-07-17T14:30:46.345678] Log entry #3: Application is running
[2025-07-17T14:30:58.456789] Log entry #4: Application is running
[2025-07-17T14:31:10.567890] Log entry #5: Application is running
[2025-07-17T14:31:22.678901] Log entry #6: Application is running
[2025-07-17T14:31:34.789012] Log entry #7: Application is running
[2025-07-17T14:31:46.890123] Log entry #8: Application is running
[2025-07-17T14:31:58.901234] Log entry #9: Application is running
[2025-07-17T14:32:10.012345] Log entry #10: Application is running
Logger completed after 2 minutes with 10 log entries.
```

The same output is written to the log file and journald (if enabled).

### Viewing Journald Logs

If you've enabled journald logging, you can view the logs using the `journalctl` command:

```
# View all logs from the simple-logger application
journalctl -f SYSLOG_IDENTIFIER=simple-logger

# View logs from the last 10 minutes
journalctl -f SYSLOG_IDENTIFIER=simple-logger --since "10 minutes ago"

# View logs with additional fields
journalctl -f SYSLOG_IDENTIFIER=simple-logger -o verbose
```

If you've set a custom SYSLOG_IDENTIFIER, replace "simple-logger" with your custom identifier in the commands above:

```
# Example with custom identifier
journalctl -f SYSLOG_IDENTIFIER=my-application
```

If you don't see any logs in journald, check the following:

1. Ensure the `systemd-devel` package is installed
2. Verify that the `systemd-python` package is installed correctly
3. Make sure you're running the script with sufficient permissions
4. Check if the script reports "Successfully imported systemd.journal module" at startup
5. Look for any "Error sending to journald" messages in the console output
