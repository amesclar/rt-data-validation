#!/bin/bash

# Configuration
LOG_DIR="test_data"
VALIDATOR_SCRIPT="rt-data-validation.py"

echo "===================================================="
echo "Regatta Timer Automated Batch Validation"
echo "===================================================="

# Check if the python script exists
if [[ ! -f "$VALIDATOR_SCRIPT" ]]; then
    echo "Error: $VALIDATOR_SCRIPT not found in current directory."
    exit 1
fi

# Find all TEST logs and look for matching SUT logs
for test_log in "$LOG_DIR"/TEST-*.log; do
    # Extract the timestamp part of the filename
    # e.g., from TEST-2025-12-19_10-59-49.log it extracts 2025-12-19_10-59-49
    timestamp=$(echo "$test_log" | grep -oP '\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')
    
    sut_log="$LOG_DIR/SUT-$timestamp.log"

    if [[ -f "$sut_log" ]]; then
        echo "Processing: $timestamp"
        python3 "$VALIDATOR_SCRIPT" --test-log "$test_log" --sut-log "$sut_log"
        
        if [ $? -eq 0 ]; then
            echo "RESULT: [ PASS ]"
        else
            echo "RESULT: [ FAIL ]"
        fi
        echo "----------------------------------------------------"
    else
        echo "Warning: Found TEST log for $timestamp but no matching SUT log."
    fi
done

echo "Batch processing complete."