import sys

def write_headers(f):
    f.write("#include <stdio.h>\n")
    f.write("#include <unistd.h>\n")
    f.write("#include <stdlib.h>\n")
    f.write("#include <errno.h>\n")
    f.write("#include <stdbool.h>\n")
    f.write("#include <sys/resource.h>\n")
    f.write("#include <linux/bpf.h>\n")
    f.write("#include <bpf/libbpf.h>\n")
    f.write("#include <bpf/bpf.h>\n")
    f.write("#include <execinfo.h>\n")
    f.write("#include <signal.h>\n")
    f.write("#include <fcntl.h>\n\n")

def write_headers_perf(f):
    f.write("#include <linux/perf_event.h>\n")
    f.write("#include <sys/syscall.h>\n\n")

def write_headers_nmi(f):
    f.write("#define DEBUGFS_TRIGGER_PATH \"/sys/kernel/debug/example_nmi_handler/trigger_nmi\"\n\n")

def write_utils(f):
    f.write("static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args) {\n")
    f.write("\treturn vfprintf(stderr, format, args);\n}\n\n")
    f.write("static volatile bool exiting = false;\n")
    f.write("static void sig_handler(int sig) {\n")
    f.write("\texiting = true;\n}\n\n")

def write_perf_utils(f):
    f.write("static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags)\n")
    f.write("{\n")
    f.write("\tint ret;\n")
    f.write("\tret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);\n")
    f.write("\treturn ret;\n")
    f.write("}\n")

def write_main_normal(f, poc_name):
    f.write("int main(int argc, char **argv)\n")
    f.write("{\n")
    f.write("int err;\n")
    f.write("libbpf_set_print(libbpf_print_fn);\n\n")

    f.write("signal(SIGINT, sig_handler);\n")
    f.write("signal(SIGTERM, sig_handler);\n\n")
    
    f.write("const char *obj_file1 = \""+poc_name+".bpf.o\";\n")
    f.write("struct bpf_object *obj1 = bpf_object__open_file(obj_file1, NULL);\n")
    f.write("if (!obj1)\n")
    f.write("\treturn 1;\n\n")

    f.write("err = bpf_object__load(obj1);\n")
    f.write("if (err) {\n")
    f.write("\tfprintf(stderr, \"Error loading BPF target object\\n\");\n")
    f.write("\treturn 1;\n")
    f.write("}\n\n")

    f.write("struct bpf_program *prog1 = bpf_object__find_program_by_name(obj1, \"test_prog1\");\n")
    f.write("if (!prog1) {\n")
    f.write("\tfprintf(stderr, \"Error finding BPF program 1 by title\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("struct bpf_program *prog2 = bpf_object__find_program_by_name(obj1, \"test_prog2\");\n")
    f.write("if (!prog2) {\n")
    f.write("\tfprintf(stderr, \"Error finding BPF program 2 by title\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("struct bpf_link *link1 = bpf_program__attach(prog1);\n")
    f.write("if (!link1) {\n")
    f.write("\tfprintf(stderr, \"Error attaching prog1\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("struct bpf_link *link2 = bpf_program__attach(prog2);\n")
    f.write("if (!link2) {\n")
    f.write("\tfprintf(stderr, \"Error attaching kprobe\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

def write_main_perf(f, poc_name):
    f.write("int main(int argc, char **argv)\n")
    f.write("{\n")
    f.write("const char *online_cpus_file = \"/sys/devices/system/cpu/online\";\n")
    f.write("int num_cpus, num_online_cpus;\n")
    f.write("bool *online_mask = NULL;\n")
    f.write("int err;\n\n")

    f.write("signal(SIGINT, sig_handler);\n")
    f.write("signal(SIGTERM, sig_handler);\n\n")

    f.write("num_cpus = libbpf_num_possible_cpus();\n")
    f.write("if (num_cpus <= 0) {\n")
    f.write("\tfprintf(stderr, \"Fail to get the number of processors\\n\");\n")
    f.write("\terr = -1;\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("struct perf_event_attr attr;\n")
    f.write("attr.type = PERF_TYPE_HARDWARE;\n")
    f.write("attr.config = PERF_COUNT_HW_CPU_CYCLES;\n")
    f.write("attr.sample_freq = 10;\n")
    f.write("attr.inherit = 1;\n")
    f.write("attr.freq = 1;\n\n")

    f.write("int cpu = 0;\n")
    f.write("int pefd = perf_event_open(&attr, -1, cpu, -1, PERF_FLAG_FD_CLOEXEC);\n")
    f.write("if (pefd < 0) {\n")
    f.write("\tfprintf(stderr, \"Fail to set up performance monitor on a CPU/Core\\n\");\n")
    f.write("\terr = -1;\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("const char *obj_file1 = \""+poc_name+"poc.bpf.o\";\n")
    f.write("struct bpf_object *obj1 = bpf_object__open_file(obj_file1, NULL);\n")
    f.write("if (!obj1)\n")
    f.write("\treturn 1;\n\n")


    f.write("err = bpf_object__load(obj1);\n")
    f.write("if (err) {\n")
    f.write("\tfprintf(stderr, \"Error loading BPF target object\\n\");\n")
    f.write("\treturn 1;\n")
    f.write("}\n\n")

    f.write("struct bpf_program *prog1 = bpf_object__find_program_by_name(obj1, \"test_prog1\");\n")
    f.write("if (!prog1) {\n")
    f.write("\tfprintf(stderr, \"Error finding BPF program by title\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

    f.write("struct bpf_program *prog2 = bpf_object__find_program_by_name(obj1, \"test_prog2\");\n")
    f.write("if (!prog2) {\n")
    f.write("\tfprintf(stderr, \"Error finding BPF program by title\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")


    f.write("struct bpf_link *link1 = bpf_program__attach_perf_event(prog1, pefd);\n")
    f.write("if (!link1) {\n")
    f.write("\tfprintf(stderr, \"Error attaching prog1\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")


    f.write("struct bpf_link *link2 = bpf_program__attach(prog2);\n")
    f.write("if (!link2) {\n")
    f.write("\tfprintf(stderr, \"Error attaching kprobe\\n\");\n")
    f.write("\tgoto cleanup;\n")
    f.write("}\n\n")

def write_trigger_nmi(f):
    f.write("int fd;\n")
    f.write("const char *data = \"1\";\n")
    f.write("ssize_t bytes_written;\n\n")

    f.write("fd = open(DEBUGFS_TRIGGER_PATH, O_WRONLY);\n")
    f.write("if (fd < 0) {\n")
    f.write("\tperror(\"Failed to open trigger file\");\n")
    f.write("}\n\n")

    f.write("bytes_written = write(fd, data, sizeof(data));\n")
    f.write("if (bytes_written < 0) {\n")
    f.write("\tperror(\"Failed to write to trigger file\");\n")
    f.write("\tclose(fd);\n")
    f.write("}\n\n")

    f.write("printf(\"Successfully triggered NMI handler.\");\n\n")

    f.write("if (fd)\n")
    f.write("\tclose(fd);\n\n")



def write_ending(f): 
    f.write("printf(\"Started successfully\");\n")
    f.write("int i;\n")
    f.write("for (i=0; i<4; i+=1) { sleep(3); }\n")
    f.write("bpf_link__destroy(link1);\n")
    f.write("bpf_link__destroy(link2);\n\n")

    f.write("cleanup:\n")
    f.write("bpf_object__close(obj1);\n")
    f.write("return 0;\n")
    f.write("}\n\n")




def write_loader(prog_type1, prog_type2, poc_name):
    print(prog_type1+" "+prog_type2)
    
    perf = 0
    if prog_type1 == 'perf_event':
        perf = 1
    
    knmi = 0
    if 'kprobe' in prog_type1 and 'my_nmi_handler' in prog_type1:
        knmi = 1
    
    file = open("output/"+poc_name+".c", "w")

    write_headers(file)
    if perf:
        write_headers_perf(file)
    if knmi:
        write_headers_nmi(file)
    
    write_utils(file)
    if perf:
        write_perf_utils(file)
    
    if perf:
        write_main_perf(file, poc_name)
    else:
        write_main_normal(file, poc_name)
    
    if knmi:
        write_trigger_nmi(file)

    write_ending(file)

if __name__ == "__main__":
    write_loader(sys.argv[1], sys.argv[2], sys.argv[3])


