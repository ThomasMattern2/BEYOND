#!/bin/bash

# Base directory containing the function directories
base_dir="./functions"

# Loop through each subdirectory in the base directory
for dir in "$base_dir"/*; do
    if [ -d "$dir" ]; then # Check if it's a directory
        echo "Running 'juni build' in $dir..."
        cd "$dir" && juni build
        cd - > /dev/null # Go back to the previous directory quietly
    fi
done

echo "Completed running 'juni build' in all directories."
