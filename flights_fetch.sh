#!/bin/bash

# Set the log file to be in the same directory as the script, unless overridden
LOGFILE="${LOGFILE:-$(dirname "$0")/airtraffic_cron.log}"

# Log current date and time
echo "===== $(date) =====" >> "$LOGFILE"

# Run the Python script using Git Bash–kompatible Pfade
"/c/Users/Fabian/AppData/Local/Programs/Python/Python313/python.exe" -u "/c/Users/Fabian/Documents/GitHub/Airtraffic/load_flights.py" >> "$LOGFILE" 2>&1

# Check if the Python script executed successfully
if [ $? -eq 0 ]; then
    echo "[✓] Script executed successfully" | tee -a "$LOGFILE"
else
    echo "[✗] Error executing script" | tee -a "$LOGFILE"
fi

