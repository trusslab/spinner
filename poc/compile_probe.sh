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

%{
static inline void s2e_make_symbolic(void *buf, int size, const char *name)
{
 __asm__ __volatile__(
   ".byte 0x0f, 0x3f\n"
   ".byte 0x00, 0x03, 0x00, 0x00\n"
   ".byte 0x00, 0x00, 0x00, 0x00\n"
   : : "a" (buf), "b" (size), "c" (name)
 );
}
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

%{#include <linux/bpf.h>%}
%{#include <linux/skbuff.h>%}
%{#include <linux/tcp.h>%}
%{#include <linux/sched.h>%}
%{#include <linux/cgroup-defs.h>%}
%{#include <linux/fs.h>%}
%{#include <linux/ip.h>%}
%{#include <linux/binfmts.h>%}
%{#include <linux/path.h>%}
%{#include <linux/seq_file.h>%}
%{#include <net/xdp.h>%}
%{#include <net/sock.h>%}
%{#include <linux/socket.h>%}
%{#include <asm/ptrace.h>%}

EOF
}

function write_inject_symbolic_map_fields {
         probe_content+="function s2e_inject_symbolic_map_fields(bpf_map: long) %{"
	 probe_content+=$'\n'
	 probe_content+="struct bpf_map *map = (struct bpf_map *) THIS->l_bpf_map;"
	 probe_content+=$'\n'
	 probe_content+="s2e_make_symbolic(&map->max_entries, sizeof(map->max_entries), \"max_entries\");"
	 probe_content+=$'\n'
	 probe_content+="s2e_make_symbolic(&map->map_flags, sizeof(map->map_flags), \"bpf_map_flags\");"
	 probe_content+=$'\n'
         probe_content+="%}"
         probe_content+=$'\n'
	 probe_content+=$'\n'
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
	
	main_function_content+="probe kernel.function(\"$poc_helper\") {"
	main_function_content+=$'\n'
	main_function_content+="s2e_message(\"$poc_helper\")"
	main_function_content+=$'\n'


	for i in "${!argument_names[@]}"; do
		echo "${argument_types[$i]} ${argument_names[$i]}" 
		if [[ "${argument_names[$i]}" == "map" ]]; then
			write_inject_symbolic_map_fields
			main_function_content+="s2e_inject_symbolic_map_fields(\$map);"
			main_function_content+=$'\n'
		elif [[ "${argument_names[$i]}" == "key" ]]; then
			main_function_content+="s2e_make_symbolic(\$key, %{sizeof(int) %}, \"key\");"
			main_function_content+=$'\n'
		elif [[ "${argument_names[$i]}" == "value" ]]; then
			main_function_content+="s2e_make_symbolic(\$value, %{sizeof(int) %}, \"value\");"
			main_function_content+=$'\n'
		else
			if [[ "${argument_types[$i]}" == *"*"* ]]; then
				object_type="${argument_types[$i]//\*/}"
				if [[ "$object_type" == "void " ]]; then
					main_function_content+="s2e_make_symbolic(\$${argument_names[$i]}, 1, \"${argument_names[$i]}\")"
					main_function_content+=$'\n'
				else
					main_function_content+="s2e_make_symbolic(\$${argument_names[$i]}, %{sizeof($object_type)%}, \"${argument_names[$i]}\")"
                        		main_function_content+=$'\n'
				fi
			fi
		fi

	done
	
	main_function_content+="}"

	
	cd $s2e_project_dir
	echo -e "$probe_content" >> $probe_file
	echo -e "$main_function_content" >> $probe_file

}

cd $s2e_project_dir
write_s2e_functions
find_and_write_helper_arguments

docker run --rm  -v $HOME:$HOME linux-build-x86_64 -c "dpkg -i /home/priya/s2e/images/.tmp-output/linux-6.8.2-x86_64/*.deb && cd $s2e_project_dir && sudo stap -a x86_64 -r 6.8.2-s2e -g -m probe probe.stp -F && cd /home/priya/defogger/poc/nmi_example && make && cp nmi_example.ko $s2e_project_dir" 
