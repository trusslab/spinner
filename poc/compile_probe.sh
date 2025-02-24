#!/bin/bash

poc_binary=$1
poc_helper=$2
poc_dir=/home/priya/defogger/poc
s2e_dir=/home/priya/s2e
s2e_project_dir=$s2e_dir/projects/$poc_binary

probe_file="probe.stp"

function write_s2e_functions {
cat <<EOF > "$probe_file"
function s2e_message(message:string) %{
 __asm__ __volatile__(
".byte 0x0f, 0x3f\n"
".byte 0x00, 0x10, 0x00, 0x00\n"
".byte 0x00, 0x00, 0x00, 0x00\n"
: : "a" (THIS->l_message)
);
%}

function s2e_make_symbolic(buf: long, size: long, name: string) %{
 __asm__ __volatile__(
".byte 0x0f, 0x3f\n"
".byte 0x00, 0x03, 0x00, 0x00\n"
".byte 0x00, 0x00, 0x00, 0x00\n"
: : "a" ((uint32_t)THIS->l_buf), "b" ((uint32_t)THIS->l_size), "c" (THIS->l_name)
: "memory"
);
%}
EOF
}

function find_and_write_helper_arguments {
	cd $poc_dir
	params=$(python3 prereq.py $poc_helper)

	arg_list=$(echo "$params" | grep -oP "\[.*\]" | tr -d "[" | tr -d "]" | tr -d "'" )
	arg_names=$(echo "$arg_list" | awk -F',' '{for (i=1; i<=NF; i++) print $i}' | awk '{print $NF}')
	arg_names=$(echo "$arg_names" | tr -d "*")
	arg_names=$(echo "$arg_names" | tr '\n' ' ')

	IFS=' ' read -r -a argument_names <<< "$arg_names"

	# Split the string by commas and preserve the parts
	IFS=',' read -ra parts <<< "$arg_list"
	argument_types=()
	# Loop through and process each part
	for part in "${parts[@]}"; do
  		# Trim leading and trailing spaces
  		part=$(echo $part | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

  		# If the last word contains '*', replace it with '*'
  		if [[ "$part" =~ \* ]]; then
  			part=$(echo "$part" | sed 's/\([[:alnum:]_]*\)[[:space:]]*[^[:space:]]*$/\1/')
  			part="${part} *"
  		else
    		# Otherwise, remove the last word
    		part=$(echo "$part" | sed 's/\([[:alnum:]_]*\)[[:space:]]*[^[:space:]]*$/\1/')
  		fi
		argument_types+=("$part")
	done
	

	probe_content=""
	probe_content+=$'\n'
	probe_content+="probe kernel.function(\"$poc_helper\") {"
	probe_content+=$'\n'
	probe_content+="s2e_message(\"$poc_helper\")"
	probe_content+=$'\n'

	echo "${argument_names[@]}"
	echo "${argument_types[@]}"
	for i in "${!argument_names[@]}"; do
		if [[ "${argument_types[$i]}" == *"struct"* ]]; then
			if [[ "${argument_types[$i]}" == *"*"* ]]; then
				arg_type=$(echo "${argument_types[$i]}" | tr -d "*")
			else
				arg_type="${argument_types[$i]}"
			fi	
			probe_content+="s2e_make_symbolic(\$${argument_names[$i]}, %{sizeof(\"$arg_type\") %}, \"${argument_names[$i]}\")"
		elif [[ "${argument_types[$i]}" == *"void"* && "${argument_types[$i]}" == *"*"* ]]; then
			probe_content+="s2e_make_symbolic(\$${argument_names[$i]}, %{sizeof(int) %}, \"${argument_names[$i]}\")"
		else	
			if [[ "${argument_names[$i]}" != "flags" ]]; then
				probe_content+="s2e_make_symbolic(\$${argument_names[$i]}, %{sizeof(${argument_types[$i]}) %}, \"${argument_names[$i]}\")"
		
			fi
		fi

		probe_content+=$'\n'
	done
	probe_content+="}"

	cd $s2e_project_dir
	echo -e "$probe_content" >> $probe_file

}

cd $s2e_project_dir
write_s2e_functions
find_and_write_helper_arguments

docker run --rm  -v $HOME:$HOME linux-build-x86_64 -c "dpkg -i /home/priya/s2e/images/.tmp-output/linux-6.8.2-x86_64/*.deb && cd $s2e_project_dir	&& sudo stap -a x86_64 -r 6.8.2-s2e -g -m probe probe.stp -F && cd /home/priya/defogger/poc/nmi_example && make && cp nmi_example.ko $s2e_project_dir" 
