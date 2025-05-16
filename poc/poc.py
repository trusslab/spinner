from prereq import get_info
import random 
import sys
import re
import json

def get_report(report_file):
    result_file = open(report_file, "r")
    line1 = result_file.readline().split()
    line2 = result_file.readline().split()
    result_file.close()
    return (line1, line2)

def generate_headers(f):
    f.write("#include \"vmlinux.h\"\n")
    f.write("#include <linux/version.h>\n")
    f.write("#include <bpf/bpf_helpers.h>\n")
    f.write("#include <bpf/bpf_tracing.h>\n")
    f.write("#include <bpf/bpf_core_read.h>\n")
    f.write("char LICENSE[] SEC(\"license\") = \"Dual BSD/GPL\";\n\n")

def generate_kfunc_signature(f, kfunc):
    with open('kfuncs.json', 'r') as kfunc_file:
        kfunc_data = json.load(kfunc_file)
    kfunc_signature = kfunc_data[kfunc]
    kfunc_params = ', '.join(kfunc_signature[1])
    f.write(f"extern {kfunc_signature[0]} {kfunc} (")
    f.write(f"{kfunc_params}")
    f.write(") __ksym;\n\n")

def generate_map(f, map_type):
    if map_type == "BPF_MAP_TYPE_LPM_TRIE":
        f.write("struct lpm_key {\n")
        f.write("__u32 prefixlen;\n")
        f.write("__u32 data;\n")
        f.write("};\n\n")

        f.write("struct {\n")
        f.write("__uint(type, BPF_MAP_TYPE_LPM_TRIE);\n")
        f.write("__type(key, struct lpm_key);\n")
        f.write("__type(value, int);\n")
        f.write("__uint(map_flags, BPF_F_NO_PREALLOC);\n")
        f.write("__uint(max_entries, 255);\n")
        f.write("} this_map SEC(\".maps\");\n\n")
        return 
    
    if map_type == "BPF_MAP_TYPE_STACK_TRACE":
        f.write("typedef struct bpf_stack_build_id stack_trace_t[127];\n")

        f.write("struct {\n")
        f.write("__uint(type, "+map_type+");\n")
        f.write("__type(key, __u32);\n")
        f.write("__type(value, stack_trace_t);\n")
        f.write("__uint(map_flags, BPF_F_STACK_BUILD_ID);\n")
        f.write("__uint(max_entries, 8);\n")
        f.write("} this_map SEC(\".maps\");\n\n")
        return

    if map_type == "BPF_MAP_TYPE_RINGBUF":
        f.write("struct ringbuf_data {\n")
        f.write("\tint data;\n")
        f.write("};\n\n")

        f.write("struct {\n")
        f.write("__uint(type, BPF_MAP_TYPE_RINGBUF);\n")
        f.write("__uint(max_entries, 256 * 1024);\n")
        f.write("} this_map SEC(\".maps\");\n\n")
        return
   
    if map_type == "BPF_MAP_TYPE_CGRP_STORAGE":
        f.write("struct {\n")
        f.write("__uint(type, BPF_MAP_TYPE_CGRP_STORAGE);\n")
        f.write("__uint(map_flags, BPF_F_NO_PREALLOC);\n")
        f.write("__type(key, int);\n")
        f.write("__type(value, int);\n")
        f.write("} this_map SEC(\".maps\");\n\n")
        return

    f.write("struct {\n")
    f.write("__uint(type, "+map_type+");\n")
    if map_type != "BPF_MAP_TYPE_QUEUE" and map_type!= "BPF_MAP_TYPE_STACK":
        f.write("__type(key, int);\n")
    f.write("__type(value, int);\n")
    f.write("__uint(max_entries, 25);\n")
    f.write("} this_map SEC(\".maps\");\n\n")

def generate_pid_map(f, map_type):
    f.write("struct {\n")
    if map_type == "BPF_MAP_TYPE_HASH":
        f.write("__uint(type, BPF_MAP_TYPE_LRU_HASH);\n")
    else:
        f.write("__uint(type, BPF_MAP_TYPE_HASH);\n")
    f.write("__type(key, u32);\n")
    f.write("__type(value, u32);\n")
    f.write("__uint(max_entries, 1024);\n")
    f.write("} pid_map SEC(\".maps\");\n\n")
    f.write("int flag=0;\n\n")

def generate_random_param(f,param, map_type):
    if 'void' == param:
        return ''
    
    if 'struct bpf_map *' in param or "ringbuf" in param:
        return "&this_map"

    if 'key' in param.split()[-1]:
        if map_type=="BPF_MAP_TYPE_LPM_TRIE":
            f.write("struct lpm_key key = {0,1};")
            return '&key'
        if map_type=="BPF_MAP_TYPE_STACK_TRACE":
            f.write("u32 key = 1;")
            return '&key'

        if '*' in param.split()[-1]:
            var_name = "&"+param.split()[-1][1:]
        else:
            var_name = " "+param.split()[-1]
        f.write(f"int {var_name[1:]} = 0;\n")
        return var_name

    if 'value' in param.split()[-1]:
        if map_type=="BPF_MAP_TYPE_STACK_TRACE":
            f.write("u32 value = 1;")
            return '&value'
        if '*' in param.split()[-1]:
            var_name = "&"+param.split()[-1][1:]
        else:
            var_name = " "+param.split()[-1]
        f.write(f"int {var_name[1:]} = 1;\n")
        return var_name

    elif 'void *' in param:
        #f.write(f"{param.split('*')[0].strip()} {param.split()[-1]} = (void*){random.randint(1000, 9999)};\n")
        if param.split()[-1][1:]=="ctx":
            return param.split()[-1][1:]
        f.write("char "+param.split()[-1]+"[8];\n")
        if '*' in param.split()[-1]:
            return  param.split()[-1][1:]
        else:
            return param.split()[-1]
    elif 'struct cgroup' in param and map_type=="BPF_MAP_TYPE_CGRP_STORAGE":
        return "cg"
    
    elif 'flags' in param:
        f.write("u64 flags = 0;\n")
        return param.split()[-1]

    elif 'size' in param and map_type == "BPF_MAP_TYPE_RINGBUF":
        f.write("u64 size = sizeof(struct ringbuf_data);")
        return "size"

    elif 'int' in param or 'u64' in param or 'u32' in param or 'u16' in param or 'u8' in param:
        f.write(f"{param} = {random.randint(0, 10)};\n")
        return param.split()[-1]
    
    else:
        param_type = ' '.join(param.rsplit(' ', 1)[:-1]) if ' ' in param else ''
        if '*' in param:
            param_type+='*'
        f.write(f"{param} = ({param_type}){hex(random.randint(0x10000000, 0xFFFFFFFF))};\n")
        if '*' in param.split()[-1]:
            return  param.split()[-1][1:]
        else:
            return param.split()[-1]

def special_case(f, helper, function_call_params, map_type):
    fcall = "struct ringbuf_data *rdata1 = "+f"{helper}({function_call_params});\n"
    fcall += "if (!rdata1) {\n"
    fcall += "return 0;\n"
    fcall += "}\n"
    fcall += "rdata1->data = 2;\n"
    fcall += "bpf_ringbuf_submit(rdata1, 0);\n"
    return fcall

def generate_params(f, helper, params, return_type, map_type):
    var_names = [generate_random_param(f,param, map_type) for param in params]
    function_call_params = ', '.join(var_names)
    function_call = ''
    if 'void' !=return_type:
        function_call += return_type+" ret = "
    function_call += f"{helper}({function_call_params});"
    if helper == "bpf_ringbuf_reserve" or helper=="bpf_ringbuf_reserve_dynptr":
        function_call = special_case(f, helper, function_call_params, map_type)
    f.write("\n"+function_call+"\n")

def generate_main_cc(f, helper, prog_type, params, prog_number, map_type):
    f.write("SEC(\""+prog_type+"\")\n");
    f.write("int test_prog"+str(prog_number)+"(void *ctx){\n")
    param_names = generate_params(f, helper, params[1], params[0], map_type)
    f.write("bpf_printk(\"bpf_prog "+str(prog_number)+"\");\n") 
    f.write("return 0;\n");
    f.write("}\n\n");

def generate_main_nl_1(f, helper, prog_type, params, prog_number, map_type):
    f.write("SEC(\""+prog_type+"\")\n")
    f.write("int test_prog"+str(prog_number)+"(void *ctx){\n")
            
    f.write("u32 pid = bpf_get_current_pid_tgid() >> 32;\n")
    f.write("u32 *stored_pid = bpf_map_lookup_elem(&pid_map, &pid);\n")
    f.write("if (!stored_pid  || pid==0) {\n")
    f.write("\treturn 0;\n")
    f.write("}\n\n")

    f.write("if (flag==0) {\n")
    f.write("\treturn 0;\n")
    f.write("}\n\n")
    
    param_names = generate_params(f, helper, params[1], params[0], map_type)
    f.write("bpf_printk(\"bpf_prog "+str(prog_number)+"\");\n")

    f.write("return 0;\n");
    f.write("}\n\n");

def generate_main_nl_2(f, helper, prog_type, params, prog_number, map_type):
    f.write("SEC(\""+prog_type+"\")\n")
    f.write("int test_prog"+str(prog_number)+"(void *ctx){\n")
    f.write("bpf_printk(\"bpf_prog "+str(prog_number)+"\");\n")
    f.write("flag = 1;\n")

    f.write("u32 pid = bpf_get_current_pid_tgid() >> 32;\n")
    f.write("bpf_map_update_elem(&pid_map, &pid, &pid, BPF_ANY);\n")
    
    param_names = generate_params(f, helper, params[1], params[0], map_type)

    f.write("bpf_map_delete_elem(&pid_map, &pid);\n")

    f.write("return 0;\n");
    f.write("}\n\n");


def generate_cgroup_main(f, helper, prog_type, params, prog_number, map_type):
    f.write("SEC(\""+prog_type+"\")\n")
    f.write("int test_prog"+str(prog_number)+"(void *ctx){\n")
    f.write("int cg_id = bpf_get_current_cgroup_id();\n")
    f.write("struct cgroup *cg = bpf_cgroup_from_id(cg_id);\n")
    f.write("if (cg){\n")

    param_names = generate_params(f, helper, params[1], params[0], map_type)

    f.write("bpf_cgroup_release(cg);\n")
    f.write("}\n")
    f.write("return 0;\n")
    f.write("}\n\n")

def write_cgrp_storage_template(f, helper, bug_type, prog_type1, prog_type2, params, map_type):
    generate_kfunc_signature(f, "bpf_cgroup_from_id")
    generate_kfunc_signature(f, "bpf_cgroup_release")

    generate_main_cc(f, "bpf_get_current_pid_tgid", prog_type1, ['u64',['void']], 1, "none")
    generate_cgroup_main(f, helper, "fentry/bpf_get_current_pid_tgid", params, 2, map_type)
    generate_cgroup_main(f, helper, prog_type2, params, 3, map_type)


if __name__ == '__main__':
    poc_name=sys.argv[1]
    pref = sys.argv[2]
    number = re.findall(r'\d+', poc_name)[0]
    report_file = "output/report"+number+".txt"
    report = get_report(report_file)
    
    (helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper, kfunc) = get_info(report, pref)
    if not prog_type1 or not prog_type2:
        with open('output/poc_data.txt', 'w') as output_file:
            output_file.write("fail")
        sys.exit()

    f = open('output/'+poc_name+'.bpf.c', 'w')
    generate_headers(f)
    if kfunc:
        generate_kfunc_signature(f,helper)
    if map_type:
        generate_map(f, map_type)

    if helper=="bpf_cgrp_storage_get" or helper=="bpf_cgrp_storage_delete":
        write_cgrp_storage_template(f, helper, bug_type, prog_type1, prog_type2, params, map_type)
    
    else:
        if bug_type == 0:
            generate_main_cc(f, helper, prog_type1, params, 1, map_type)
            generate_main_cc(f, helper, prog_type2, params, 2, map_type)

        else:
            generate_pid_map(f, map_type)
            generate_main_nl_1(f, helper, prog_type1, params, 1, map_type)
            generate_main_nl_2(f, helper, prog_type2, params, 2, map_type)
    f.close()

    with open('output/poc_data.txt', 'w') as output_file:
        output_file.write(orig_helper+" "+prog_type1+" "+prog_type2+" "+str(bug_type))

