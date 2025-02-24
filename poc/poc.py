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
    f.write(") __ksym;")

def generate_map(f, map_type, extra):
    timer = extra[0]
    spin_lock = extra[1]

    f.write("struct map_elem {\n")
    f.write("int counter;\n")
    if timer:
        f.write("struct bpf_timer timer;\n")
    if spin_lock:
        f.write("struct bpf_spin_lock lock;\n")
    f.write("};\n\n")

    f.write("struct {\n")
    f.write("__uint(type, "+map_type+");\n")
    f.write("__type(key, int);\n")
    f.write("__type(value, struct map_elem);\n")
    f.write("__uint(max_entries, 25);\n")
    f.write("} this_map SEC(\".maps\");\n\n")

def generate_random_param(f,param):
    if 'struct bpf_map *' in param:
        return "&this_map"

    if 'key' in param.split()[-1] or 'value' in param.split()[-1]:
        if '*' in param.split()[-1]:
            var_name = "&"+param.split()[-1][1:]
        else:
            var_name = " "+param.split()[-1]
        f.write(f"int {var_name[1:]} = {random.randint(0, 1000)};\n")
        return var_name

    if 'value' in param.split()[-1]:
        if '*' in param.split()[-1]:
            var_name = "&"+param.split()[-1][1:]
        else:
            var_name = " "+param.split()[-1]
        f.write(f"struct map_elem {var_name[1:]} = ")
        f.write("{};\n")
        return var_name

    elif 'void *' in param:
        #f.write(f"{param.split('*')[0].strip()} {param.split()[-1]} = (void*){random.randint(1000, 9999)};\n")
        f.write("char "+param.split()[-1]+"[8];\n")
        if '*' in param.split()[-1]:
            return  param.split()[-1][1:]
        else:
            return param.split()[-1]
    
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

def generate_params(f, helper, params, return_type):
    var_names = [generate_random_param(f,param) for param in params]
    function_call_params = ', '.join(var_names)
    function_call = ''
    if 'void' !=return_type:
        function_call += return_type+" ret = "
    function_call += f"{helper}({function_call_params});"
    f.write("\n"+function_call+"\n")

def generate_main(f, helper, prog_type, params, prog_number):
    f.write("SEC(\""+prog_type+"\")\n");
    f.write("int test_prog"+str(prog_number)+"(void *ctx){\n");
    param_names = generate_params(f, helper, params[1], params[0])
    f.write("bpf_printk(\"bpf_prog "+str(prog_number)+"\");\n") 
    f.write("return 0;\n");
    f.write("}\n\n");


if __name__ == '__main__':
    poc_name=sys.argv[1]
    number = re.findall(r'\d+', poc_name)[0] 
    report_file = "output/report"+number+".txt"
    report = get_report(report_file)

    (helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper, kfunc) = get_info(report)
    f = open('output/'+poc_name+'.bpf.c', 'w')
    generate_headers(f)
    if kfunc:
        generate_kfunc_signature(f,helper)
    if map_type:
        tracing_prog_types = ['kprobe', 'perf_event', 'tp', 'tracepoint', "raw_tp.w",
                "raw_tracepoint.w", "raw_tp", "raw_tracepoint"]
        for prog_type in tracing_prog_types:     #tracing prog types cannot use bpf timers or spin locks
            if prog_type in prog_type1 or prog_type in prog_type2:
                generate_map(f, map_type, [0, 0])
            else
                generate_map(f, map_type, [1, 1])

    generate_main(f, helper, prog_type1, params, 1)
    generate_main(f, helper, prog_type2, params, 2)
    f.close()

    with open('output/poc_data.txt', 'w') as output_file:
        output_file.write(orig_helper+" "+prog_type1+" "+prog_type2+" "+str(bug_type))

