import re
import subprocess


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
    #print(split_list)
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
            '''
            readlines.pop(i+3)
            readlines.pop(i+4)
            readlines.insert(i+3 ,first_line)
            readlines.insert(i+4, insert_line)
            '''
            readlines[i+3] = first_line
            readlines[i+4] = insert_line
            break
    f.close()

    f = open ("/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c", "w")
    f.writelines(readlines)
    f.close()

    return function_name



def make():
    make_command = ['clang', '-O2', '-g', '-target', 'bpf', '-D__TARGET_ARCH_x86', '-I/home/priya/linux-6.9/tools/testing/selftests/bpf/', '-c', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.c', '-o', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.bpf.o']
    make_file = open("make_result.txt", 'w')
    subprocess.call(make_command, stderr=make_file,  shell=False)
    make_file.close()

    make_file = open('make_result.txt', 'r')
    make_result = make_file.read().replace('\n', '')
    if 'error' in make_result:
        result_file.write(f"{'yes':<20}")
    else:
        result_file.write(f"{'no':<20}")
    if 'warning' in make_result:
        result_file.write(f"{'yes':<20}")
    else:
        result_file.write(f"{'no':<20}")
    make_file.close()

def run():
    run_command = ['bpftool', 'struct_ops', 'register', '/home/priya/linux-6.9/tools/testing/selftests/bpf/progs/bpf_cubic.bpf.o']
    run_file = open("run_result.txt", "w")
    subprocess.call(run_command, stderr=run_file, shell=False)
    run_file.close()

    run_file = open("run_result.txt", "r")
    run_result = run_file.read().replace('\n', '')
    if 'unknown func' in run_result:
        result_file.write(f"{'no'}\n")
    else:
        result_file.write(f"{'yes'}\n")
    run_file.close()

    unregister_command = ['bpftool', 'struct_ops', 'unregister', 'name', 'cubic']
    subprocess.call(unregister_command, shell=False)


def restart_marker():
    marker.write("* Start of BPF helper function descriptions:")


def test_struct_ops():
    result_file = open('helper-progtype.txt','a')
    utypes = ['u8', 'u16', 'u32', 'u64', 's8', 's16', 's32', 's64']

    for i in range(216):

        helper_file = open("/home/priya/libbpf-bootstrap/examples/c/create_tests/bpf.h", "r")
        marker = open("/home/priya/libbpf-bootstrap/examples/c/create_tests/marker.txt", "r")

        marker_fn = marker.read()
        marker.close()

        marker = open("/home/priya/libbpf-bootstrap/examples/c/create_tests/marker.txt", "w")
        read_start = False
        write_marker = False

        while(True):
            line = helper_file.readline()
            if not line:
                break

            if marker_fn in line:   #found where we stopped last time
                read_start = True
                write_marker = True
                continue

            if "*/" in line and read_start == True:    #end of all function defs
                restart_marker()
                read_start = False
                continue

            if read_start==True and re.search("^ [*] ([a-z]|[A-Z]|[_])", line):         #next fn def
                if write_marker:            #need to keep track of where we ended
                    marker.write(line)
                    write_marker = False
                    helper_fn = parse_and_write_to_cubic(line)
                
                    if not helper_fn:
                        break

                    program_type = 'struct_ops'
                    result_file.write(f"{helper_fn:<40}")
                    result_file.write(f"{program_type:<40}")
                
                    make()
                    run()

                break
        helper_file.close()
        marker.close()

    result_file.close()
