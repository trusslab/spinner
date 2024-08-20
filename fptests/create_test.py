import re

def write_params(f, params):
    if len(params)==1 and  params[0]=="void":
        return
    for i in range(len(params)):
        words = params[i].split()
        temp_param_name = words.pop()
        #print(words)
        for k in range(len(words)):
            f.write(words[k]+" ")
        if '*' in temp_param_name:
            f.write("*")
        f.write(" param"+str(i)+";\n")
    return

def restart_marker(marker):
    marker.write("* Start of BPF helper function descriptions:")
    

def write_beginning(f, attach_to):
    f.write("#include \"vmlinux.h\"\n")
    f.write("#include <linux/version.h>\n")
    f.write("#include <bpf/bpf_helpers.h>\n")
    f.write("#include <bpf/bpf_tracing.h>\n")

    f.write("char LICENSE[] SEC(\"license\") = \"Dual BSD/GPL\";\n")

    f.write("SEC(\""+attach_to+"\")\n")
    if attach_to=="freplace/print":
        f.write("__noinline int test_prog(){\n")
    else:
        f.write("int test_prog(void *ctx){\n")

def write_end(f):
    f.write("return 0;\n")
    f.write("}\n")

def create_test():
    f = open ("/home/priya/defogger/fptests/output/test.bpf.c", "w")
    helper_file = open("/home/priya/defogger/fptests/bpf.h", "r")
    marker = open("/home/priya/defogger/fptests/output/marker.txt", "r")

    prog_type_file = open("/home/priya/defogger/fptests/output/prog_type.txt", "r")
    attach_to = prog_type_file.read()
    prog_type_file.close()


    marker_fn = marker.read()
    marker.close()

    marker = open("/home/priya/defogger/fptests/output/marker.txt", "w")
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
            restart_marker(marker)
            read_start = False
            continue

        if read_start==True and re.search("^ [*] ([a-z]|[A-Z]|[_])", line):         #next fn def
            if write_marker:            #need to keep track of where we ended
                marker.write(line)
                write_marker = False
            
                write_beginning(f, attach_to)

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
                #print(return_type+function_name)
                print(params)

                write_params(f, params)

                if return_type == "void":
                    f.write(function_name+"(")
                else:
                    f.write(return_type+" ret = "+function_name+"(")

                if len(params)==1 and params[0]=="void":
                    f.write(");\n")
                elif len(params)==1:
                    f.write(" param0);\n")
                else:
                    for i in range(len(params)-1):
                        f.write(" param"+str(i)+",")
                    f.write(" param"+str(i+1))
                    f.write(");\n")

                write_end(f)
            break


    f.close()
    helper_file.close()
    marker.close()



