import re
import subprocess

utypes = ['u8', 'u16', 'u32', 'u64', 's8', 's16', 's32', 's64']

def prep_file():
    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "r")
    readlines = f.readlines()
    for i in range(len(readlines)):
        if 'void BPF_PROG(bpf_cubic_init, struct sock *sk)' in readlines[i]:
            for j in range(10):
                readlines.insert(i+2, '//\n')
            break
    f.close()
    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "w")
    f.writelines(readlines)
    f.close()

def cleanup_file():
    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "r")
    readlines = f.readlines()
    for i in range(len(readlines)):
        if 'void BPF_PROG(bpf_cubic_init, struct sock *sk)' in readlines[i]:
            for j in range(6):
                readlines.pop(i+2)
            break
    f.close()
    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "w")
    f.writelines(readlines)
    f.close()

def write_params(insert_line, params):
    if len(params)==1 and  params[0]=="void":
        return insert_line
    for i in range(len(params)):
        words = params[i].split()
        temp_param_name = words.pop()
        
        for k in range(len(words)):
            if words[k] in utypes:
                insert_line+="__"
            if words[k] == 'size_t':
                insert_line+='int '
            else:
                insert_line+=words[k]
                insert_line+=" "
        if '*' in temp_param_name:
            insert_line+="*"
            insert_line+=" param"
            insert_line+=str(i)
            insert_line+="=(void *)0x28ff44;"
        else:
            insert_line+=" param"
            insert_line+=str(i)
            insert_line+="=0;"
    return insert_line

def parse_and_write_to_cubic(line):
    split_list=re.split('\(|\)|,', line)
    retfn_list = (split_list[0].split())
    return_type = retfn_list[1]
    if return_type=="struct":
        return_type+=" "
        return_type+=retfn_list[2]
        function_name = retfn_list[3]
    else:
        function_name = retfn_list[2]
    if '*' in function_name:
        return_type+=" *"
        function_name=function_name[1:]

    params = []
    for i in range(1, len(split_list)-1):
        params.append(split_list[i])

    if not function_name:
        return

    first_line = ''
    first_line += write_params(first_line, params)
    first_line +="\n"
    insert_line = ''
    if return_type == "void":
        insert_line += function_name
        insert_line+="("
    else:
        if return_type in utypes:
            insert_line+="__"
        insert_line+=return_type
        insert_line+=" ret = "
        insert_line+=function_name
        insert_line+="("
    if function_name=="bpf_trace_printk":
        insert_line+="\"hello world\");\n"
    else:
        if len(params)==1 and params[0]=="void":
            insert_line+=");"
        elif len(params)==1:
            insert_line+=" param0);"
        else:
            for i in range(len(params)-1):
                insert_line+=" param"
                insert_line+=str(i)
                insert_line+=","
            insert_line+=" param"
            insert_line+=str(i+1)
            insert_line+=");"

    if return_type!='void':
        insert_line+="if (ret) {bpf_printk(\"hello\");}\n"


    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "r")
    readlines = f.readlines()
    for i in range(len(readlines)):
        if re.search('bpf_cubic_init\"', readlines[i]):
            print(i)
            readlines[i+3] = first_line
            readlines[i+4] = insert_line
            break
    f.close()

    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "w")
    f.writelines(readlines)
    f.close()

    return function_name



def make(result_file):
    make_command = ['clang', '-O2', '-g', '-target', 'bpf', '-D__TARGET_ARCH_x86', '-I/home/priya/linux-6.9/tools/testing/selftests/bpf/', '-c', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c', '-o', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.bpf.o']
    make_result = subprocess.run(make_command, shell = False, capture_output=True, text=True).stderr

    if 'error' in make_result:
        result_file.write(f"{'yes':<15}")
    else:
        result_file.write(f"{'no':<15}")
    if 'warning' in make_result:
        result_file.write(f"{'yes':<15}")
    else:
        result_file.write(f"{'no':<15}")

def run(result_file):
    run_command = ['bpftool', 'struct_ops', 'register', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.bpf.o']
    run_result = subprocess.run(run_command, shell = False, capture_output=True, text=True).stderr

    if 'helper call might sleep in a non-sleepable prog' in run_result:
        result_file.write(f"{'yes':15}")
    else:
        result_file.write(f"{'no':15}")

    if 'unknown func' in run_result or 'program of this type cannot use' in run_result or 'helper call might sleep in a non-sleepable prog' in run_result:
        result_file.write(f"{'no'}\n")
    else:
        result_file.write(f"{'yes'}\n")

    unregister_command = ['bpftool', 'struct_ops', 'unregister', 'name', 'cubic']
    subprocess.call(unregister_command, shell=False)


def restart_marker(marker):
    marker = "* Start of BPF helper function descriptions:"
    return marker

def test_struct_ops(uapi_file):
    result_file = open('output/helper-progtype.txt','a')
    marker = "* Start of BPF helper function descriptions:"
    prep_file()
    
    for i in range(216):

        helper_file = open(uapi_file, "r")
        read_start = False
        write_marker = False

        while(True):
            line = helper_file.readline()
            if not line:
                break

            if marker in line:
                read_start = True
                write_marker = True
                continue

            if "*/" in line and read_start == True:    #end of all function defs
                marker = restart_marker(marker)
                read_start = False
                continue

            if read_start==True and re.search("^ [*] ([a-z]|[A-Z]|[_])", line):         #next fn def
                if write_marker:            #need to keep track of where we ended
                    marker = line
                    write_marker = False
                    helper_fn = parse_and_write_to_cubic(line)
                
                    if not helper_fn:
                        break

                    program_type = 'struct_ops'
                    result_file.write(f"{helper_fn:<40}")
                    result_file.write(f"{program_type:<40}")
                
                    make(result_file)
                    run(result_file)

                break
        helper_file.close()
    result_file.close()
    cleanup_file()
    

if __name__ == "__main__":
    test_struct_ops()
