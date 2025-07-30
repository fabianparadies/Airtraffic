#!/usr/bin/env zsh

# Set the log file to be in the same directory as the script, unless overridden
LOGFILE="${LOGFILE:-$(dirname "$0")/airtraffic_cron.log}"

# Log current date and time
echo "=======================================================================================" >> "$LOGFILE"
echo "===== $(date) =====" >> "$LOGFILE"

# Run the Python script
/usr/local/bin/python3 -u /Users/fabianparadies/Documents/GitHub/Airtraffic/load_flights.py >> "$LOGFILE" 2>&1

# Check if the Python script executed successfully
if [ $? -eq 0 ]; then
    echo "[✓] Script executed successfully" | tee -a "$LOGFILE"
else
    echo "[✗] Error executing script" | tee -a "$LOGFILE"
fi

