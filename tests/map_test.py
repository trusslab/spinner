import os
import subprocess

result_file = open('map-progtype.txt','w')
result_file.write(f"{'map_type':<40}{'program_type':<40}{'compile error':<20}{'compile warning':<20}{'allowed'}\n")

program_types = ['cgroup/dev'] 
'''
'cgroup/skb','cgroup_skb/egress', 'cgroup_skb/ingress', 'cgroup/getsockopt', 'cgroup/setsockopt', 'cgroup/bind4',
        'cgroup/bind6', 'cgroup/connect6', 'cgroup/getpeername6', 'cgroup/getsockname6', 'cgroup/recvmsg4', 'cgroup/sendmsg4', 'cgroup/recvmsg6',
        'cgroup/sendmsg6', 'cgroup/connect_unix', 'cgroup/sendmsg_unix', 'cgroup/recvmsg_unix', 'cgroup/getpeername_unix', 'cgroup/getsockname_unix', 
        'cgroup/post_bind4', 'cgroup/post_bind6', 'cgroup/sock_create', 'cgroup/sock', 'cgroup/sock_release', 'cgroup/sysctl',  
        'flow_dissector', 'kprobe', 'kretprobe', 'ksyscall', 'kretsyscall', 'uprobe', 'uprobe.s', 'uretprobe', 'uretprobe.s', 'usdt', 'kprobe.multi', 
        'kretprobe.multi', 'lirc_mode2', 'lsm_cgroup/socket_bind', 'lsm/task_free', 'lsm.s/bpf', 'lwt_in', 'lwt_out', 'lwt_seg6local', 
        'lwt_xmit', 'perf_event', 'raw_tp.w', 'raw_tracepoint.w', 'raw_tp', 'raw_tracepoint', 'action', 'classifier', 'tc', 'sk_lookup', 'sk_msg', 
        'sk_reuseport/migrate', 'sk_reuseport', 'sk_skb', 'sk_skb/stream_parser', 'sk_skb/stream_verdict', 'socket', 'sockops', 'syscall',
        'tp/sched/sched_switch', 'tracepoint/sched/sched_switch', 'fmod_ret/do_nanosleep', 'fmod_ret.s/bpf_fentry_test1', 'fentry/do_nanosleep', 
        'fentry.s/bpf_fentry_test1',
        'fexit/do_nanosleep', 'fexit.s/bpf_fentry_test1', 'iter/tcp', 'iter.s/cgroup', 'tp_btf/task_newtask', 'xdp.frags/cpumap', 'xdp/cpumap',
        'xdp.frags/devmap', 'xdp/devmap', 'xdp', 'xdp.frags']
'''
'''
other_program_types = ['freplace',  'struct_ops'] 
'''

map_types = []
helper_file = open('/home/priya/libbpf-bootstrap/examples/c/create_tests/bpf.h', 'r')
read_start = False
while True:
    line = helper_file.readline()
    if not line:
        break
    if "enum bpf_map_type" in line:
        read_start = True
        continue
    if "};" in line and read_start==True:
        read_start = False
        break
    if read_start==True and '*' not in line:
        if len(line.strip().split()) > 1:
            map_types.append(line.strip().split()[0])
        else:
            map_types.append(line.strip()[:-1:])
    

#print(map_types)


for program_type in program_types:

    for map_type in map_types:    
        test_file = open("map_test.bpf.c", "w")
        test_file.write("#include \"vmlinux.h\"\n")
        test_file.write("#include <linux/version.h>\n")
        test_file.write("#include <bpf/bpf_helpers.h>\n")
        test_file.write("char LICENSE[] SEC(\"license\") = \"Dual BSD/GPL\";\n")

        test_file.write("struct {\n")
        test_file.write("__uint(type, ")
        test_file.write(map_type)
        test_file.write(");\n")
        test_file.write("__uint(max_entries, 1);\n")
        test_file.write("__type(key, __u32);\n")
        test_file.write("__type(value, __u64);\n")
        test_file.write("} this_map SEC(\".maps\");\n\n")

        test_file.write("SEC(\"")
        test_file.write(program_type)
        test_file.write("\")\n")
        test_file.write("int test_prog(void *ctx){\n")
        test_file.write("__u32 v0 = 0;\n")
        test_file.write("__u64 v1 = 0;\n")
        test_file.write("bpf_printk(\"hello\");\n")
        test_file.write("return 0;\n")
        test_file.write("}\n")
        test_file.close()

        result_file.write(f"{map_type:<40}")
        result_file.write(f"{program_type:<40}")
        
        #os.system('sudo make test 2>make_result.txt')
        make_command = ['make', 'map_test']
        make_file = open("/home/priya/libbpf-bootstrap/examples/c/create_tests/make_result.txt", 'w')
        subprocess.call(make_command, stderr=make_file, shell=False)
        make_file.close()
        
        
        make_file = open("/home/priya/libbpf-bootstrap/examples/c/create_tests/make_result.txt", 'r')
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

        
        #os.system('sudo ./test &>run_result.txt')
        run_file = open("create_tests/run_result.txt", 'w')
        subprocess.call('./map_test', stderr = run_file, shell=False)
        run_file.close()

        run_file = open("create_tests/run_result.txt", "r")
        run_result = run_file.read().replace('\n', '')
        print(run_result)
        
        if 'Failed to load and verify BPF skeleton' in run_result:
            result_file.write(f"{'no'}\n")
        else:
            result_file.write(f"{'yes'}\n")
        run_file.close()
        
        
result_file.close()
