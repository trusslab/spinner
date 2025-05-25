#!/bin/bash

source config.conf

input_file=$REPORT_FILE
report="all"

while getopts "i:r:p:" opt; do
    case "$opt" in
        i) input_file="$OPTARG" ;;  # Assign value for -i (input_file)
        r) report="$OPTARG" ;;  # Assign value for -r (report)
	p) pref="$OPTARG" ;; # preferred prog type for nested locking bug
        ?) echo "Usage: $0 [-i input_file] [-r report]"; exit 1 ;;
    esac
done

# Ensure the input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: File '$input_file' not found!"
    exit 1
fi

if [[ $report == "all" ]]; then
	counter=1
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
else
	line1_number=$((report * 3 - 2))
	line2_number=$((report * 3 - 1))
	line3_number=$((report * 3))


	line1=$(sed -n "${line1_number}p" "$input_file")
	line2=$(sed -n "${line2_number}p" "$input_file")
	line3=$(sed -n "${line3_number}p" "$input_file")

	output_file="output/report$report.txt"
	echo "$line1" > "$output_file"
	echo "$line2" >> "$output_file"
	echo "$line3" >> "$output_file"

	if [[ "$line1" == *nested* ]]; then
		if [[ "$pref" == kprobe ]]; then
			./create_poc.sh "poc${report}_kprobe" "kprobe"&
                	wait
		elif [[ "$pref" == fentry ]]; then
			./create_poc.sh "poc${report}_fentry" "fentry"&
			wait
		elif [[ "$pref" == fentry_unlock ]]; then
			./create_poc.sh "poc${report}_fentry_unlock" "fentry/unlock"&
			wait
		elif [[ "$pref" == tracepoint ]]; then
			./create_poc.sh "poc${report}_tracepoint" "tracepoint"&
			wait
		else 
			./create_poc.sh "poc${report}_kprobe" "kprobe"&
			wait
			./create_poc.sh "poc${report}_fentry" "fentry"&
			wait
			./create_poc.sh "poc${report}_fentry_unlock" "fentry/unlock"&
			wait
			./create_poc.sh "poc${report}_tracepoint" "tracepoint"&
			wait
		fi
	else
		./create_poc.sh "poc$report" "none"&
		wait
	fi
fi

