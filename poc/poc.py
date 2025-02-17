from prereq import get_info
import random 

def get_report():
    result_file = open("../graphtraverse/file69", "r")
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

def generate_map(f, map_type):
    f.write("struct {\n")
    f.write( "__uint(type, "+map_type+");\n")
    f.write("__type(key, int);\n")
    f.write("__type(value,int);\n")
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

    elif 'const void *' in param:
        f.write(f"{param.split('*')[0].strip()} {param.split()[-1]} = (void*){random.randint(1000, 9999)};\n")
        if '*' in param.split()[-1]:
            return  param.split()[-1][1:]
        else:
            return param.split()[-1]
    
    elif 'u64' in param:
        f.write(f"{param} = {random.randint(0, 10)};\n")
        return param.split()[-1]
    
    else:
        print("unknown param")
        return ''

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
    f.write("}");


if __name__ == '__main__':
    report = get_report()
    (helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper) = get_info(report)
    
    f = open('output/poc.bpf.c', 'w')
    generate_headers(f)
    generate_map(f, map_type)
    generate_main(f, helper, prog_type1, params, 1)
    generate_main(f, helper, prog_type2, params, 2)
    f.close()

    with open('output/poc_data.txt', 'w') as output_file:
        output_file.write(orig_helper+" "+prog_type1+" "+prog_type2)

