#!/bin/bash

if [[ -z "$1" ]]; then
    input_file="../graphtraverse/file69"
else
    input_file="$1"
fi

counter=1

# Ensure the input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

# Read the file line by line
while IFS= read -r line1; do
    # Read 2 more lines if available
    IFS= read -r line2 || line2=""
    IFS= read -r line3 || line3=""

    # Create output file for each 3-line set
    output_file="output/report$counter.txt"
    echo "$line1" > "$output_file"
    [[ -n "$line2" ]] && echo "$line2" >> "$output_file"
    [[ -n "$line3" ]] && echo "$line3" >> "$output_file"
    # Run the create_poc.sh script
    ./create_poc.sh "poc$counter"&
    wait
    # Uncomment this line if you want to remove the file after processing
    # rm "$output_file"

    echo $counter
    # Increment the counter for each batch of 3 lines
    ((counter++))
done < "$input_file"
