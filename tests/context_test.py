import subprocess

program_types = ['cgroup/dev', 'cgroup/skb','cgroup_skb/egress', 'cgroup_skb/ingress', 'cgroup/getsockopt', 'cgroup/setsockopt', 'cgroup/bind4',
                'cgroup/bind6', 'cgroup/connect6', 'cgroup/getpeername6', 'cgroup/getsockname6', 'cgroup/recvmsg4', 'cgroup/sendmsg4', 'cgroup/recvmsg6',
                'cgroup/sendmsg6', 'cgroup/connect_unix', 'cgroup/sendmsg_unix', 'cgroup/recvmsg_unix', 'cgroup/getpeername_unix', 'cgroup/getsockname_unix',
                'cgroup/post_bind4', 'cgroup/post_bind6', 'cgroup/sock_create', 'cgroup/sock', 'cgroup/sock_release', 'cgroup/sysctl',                
                'flow_dissector', 'kprobe', 'kretprobe', 'ksyscall', 'kretsyscall', 'uprobe', 'uprobe.s', 'uretprobe', 'uretprobe.s', 'usdt', 'kprobe.multi',
                'kretprobe.multi', 'lirc_mode2', 'lsm_cgroup/socket_bind', 'lsm/task_free', 'lsm.s/bpf', 'lwt_in', 'lwt_out', 'lwt_seg6local',
                'lwt_xmit', 'perf_event', 'raw_tp.w', 'raw_tracepoint.w', 'raw_tp', 'raw_tracepoint', 'action', 'classifier', 'tc', 'sk_lookup', 'sk_msg',
                'sk_reuseport/migrate', 'sk_reuseport', 'sk_skb', 'sk_skb/stream_parser', 'sk_skb/stream_verdict', 'socket', 'sockops', 'syscall',
                'tp/sched/sched_switch', 'tracepoint/sched/sched_switch', 'fmod_ret/bpf_modify_return_test', 'fmod_ret.s/bpf_fentry_test1', 
                'fentry/do_nanosleep', 'fentry.s/bpf_fentry_test1', 'fexit/do_nanosleep', 'fexit.s/bpf_fentry_test1', 'iter/tcp', 'iter.s/cgroup', 
                'tp_btf/task_newtask', 'xdp.frags/cpumap', 'xdp/cpumap', 'xdp.frags/devmap', 'xdp/devmap', 'xdp', 'xdp.frags']

'''
other_program_types = ['freplace',  'struct_ops']
'''

for program_type in program_types:
    f = open('context_test.bpf.c', 'w')
    f.write("#include \"vmlinux.h\"\n")
    f.write("#include <linux/version.h>\n")
    f.write("#include <bpf/bpf_helpers.h>\n")
    f.write("char LICENSE[] SEC(\"license\") = \"Dual BSD/GPL\";\n")

    f.write("SEC(\""+program_type+"\")\n")
    f.write("int test_prog(void *ctx){\n")
    f.write("bpf_printk(\"hello\");\n")
    f.write("return 1;\n")
    f.write("}\n")

    f.close()

    make_command = ['make', 'context_test']
    make_file = open("make_result.txt", 'w')
    subprocess.call(make_command, stderr=make_file, shell=False)
    make_file.close()

    make_file = open('make_result.txt', 'r')
    make_result = make_file.read().replace('\n', '')
    if 'error' in make_result or 'warning' in make_result:
        print(make_result)
        make_file.close()
        break
    make_file.close()
    

    
    run_file = open("run_result.txt", 'w')
    subprocess.call('./context_test', stdout=run_file, shell=False)
    run_file.close()

    run_file = open("run_result.txt", "r")
    run_result = run_file.read().replace('\n', '')
    if "Successfully started!" not in run_result:
        run_file.close()
        break
    run_file.close()

