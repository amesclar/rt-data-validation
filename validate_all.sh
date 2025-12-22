#!/bin/bash

# Configuration
LOG_DIR="test_data"
VALIDATOR_SCRIPT="rt_data_validation.py" # Updated filename

echo "===================================================="
echo "Regatta Timer Automated Batch Validation"
echo "===================================================="

# Check if the python script exists
if [[ ! -f "$VALIDATOR_SCRIPT" ]]; then
    echo "Error: $VALIDATOR_SCRIPT not found."
    exit 1
fi

for test_log in "$LOG_DIR"/TEST-*.log; do
    timestamp=$(echo "$test_log" | grep -oP '\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}')
    sut_log="$LOG_DIR/SUT-$timestamp.log"

    if [[ -f "$sut_log" ]]; then
        echo "Processing: $timestamp"
        python3 "$VALIDATOR_SCRIPT" --test-log "$test_log" --sut-log "$sut_log"
        
        if [ $? -eq 0 ]; then
            echo "RESULT: [ PASS ]"
        else
            echo "RESULT: [ FAIL ] (Check .failures.txt for details)"
        fi
        echo "----------------------------------------------------"
    fi
done