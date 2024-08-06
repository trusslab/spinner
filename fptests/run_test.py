import os
import subprocess

result_file = open('output/helper-progtype.txt','w')
result_file.write(f"{'function_name':<40}{'program_type':<40}{'compile error':<20}{'compile warning':<20}{'allowed'}\n")

program_types = ['cgroup/dev', 'cgroup/skb','cgroup_skb/egress', 'cgroup_skb/ingress', 'cgroup/getsockopt', 'cgroup/setsockopt', 'cgroup/bind4',
        'cgroup/bind6', 'cgroup/connect6', 'cgroup/getpeername6', 'cgroup/getsockname6', 'cgroup/recvmsg4', 'cgroup/sendmsg4', 'cgroup/recvmsg6',
        'cgroup/sendmsg6', 'cgroup/connect_unix', 'cgroup/sendmsg_unix', 'cgroup/recvmsg_unix', 'cgroup/getpeername_unix', 'cgroup/getsockname_unix', 
        'cgroup/post_bind4', 'cgroup/post_bind6', 'cgroup/sock_create', 'cgroup/sock', 'cgroup/sock_release', 'cgroup/sysctl',  
        'flow_dissector', 'kprobe', 'kretprobe', 'ksyscall', 'kretsyscall', 'uprobe', 'uprobe.s', 'uretprobe', 'uretprobe.s', 'usdt', 'kprobe.multi', 
        'kretprobe.multi', 'lirc_mode2', 'lsm_cgroup/socket_bind', 'lsm/task_free', 'lsm.s/bpf', 'lwt_in', 'lwt_out', 'lwt_seg6local', 
        'lwt_xmit', 'perf_event', 'raw_tp.w', 'raw_tracepoint.w', 'raw_tp', 'raw_tracepoint', 'action', 'classifier', 'tc', 'sk_lookup', 'sk_msg', 
        'sk_reuseport/migrate', 'sk_reuseport', 'sk_skb', 'sk_skb/stream_parser', 'sk_skb/stream_verdict', 'socket', 'sockops', 'syscall',
        'tp/sched/sched_switch', 'tracepoint/sched/sched_switch', 'fmod_ret/bpf_modify_return_test', 'fmod_ret.s/bpf_fentry_test1', 'fentry/do_nanosleep', 
        'fentry.s/bpf_fentry_test1',
        'fexit/do_nanosleep', 'fexit.s/bpf_fentry_test1', 'freplace/print', 'iter/tcp', 'iter.s/cgroup', 'tp_btf/task_newtask', 'xdp.frags/cpumap', 
        'xdp/cpumap', 'xdp.frags/devmap', 'xdp/devmap', 'xdp', 'xdp.frags']



for program_type in program_types:

    prog_type_file = open("output/prog_type.txt", "w")
    prog_type_file.write(program_type)
    prog_type_file.close()
    
    for i in range(216):
        os.system('python3 create_test.py')
        test_helper_fn = ''
        result_line = ''

        test_file = open("output/test.bpf.c", "r")
        while True:
            line = test_file.readline()
            if not line:
                break
            if "bpf_" in line and "(" in line :
                if "=" in line:
                    test_helper_fn+=line[line.index('=')+2:line.index('(')]
                else:
                    test_helper_fn+=line[line.index('bpf'):line.index('(')]
        print(test_helper_fn)
        if not test_helper_fn:
            continue
        result_file.write(f"{test_helper_fn:<40}")
        written_prog_type = program_type
        strip_names = ['lsm_cgroup/socket_bind', 'lsm/task_free', 'lsm.s/bpf', 'tp/sched/sched_switch', 'tracepoint/sched/sched_switch', 
                'fmod_ret/bpf_modify_return_test', 'fmod_ret.s/bpf_fentry_test1', 'fentry/do_nanosleep', 'fentry.s/bpf_fentry_test1',
                'fexit/do_nanosleep', 'fexit.s/bpf_fentry_test1', 'freplace/print', 'iter/tcp', 'iter.s/cgroup', 'tp_btf/task_newtask']
        if written_prog_type in strip_names:
            written_prog_type = written_prog_type.split('/')[0]
        result_file.write(f"{written_prog_type:<40}")

       
        make_command = ['clang', '-O2', '-g', '-target', 'bpf', '-D__TARGET_ARCH_x86', '-c', 'output/test.bpf.c', '-o', 'output/test.bpf.o']
        make_file = open("output/make_result.txt", 'w')
        subprocess.call(make_command, stderr=make_file, shell=False)
        
        if program_type == "freplace/print":
            make_command = ['gcc', '-o', 'output/freplace', 'output/freplace.c', '-lbpf']
            subprocess.call(make_command, stderr = make_file, shell=False)

        else:
            make_command = ['gcc', '-o', 'output/test', 'output/test.c', '-lbpf']
            subprocess.call(make_command, stderr = make_file, shell=False)

        make_file.close()


        make_file = open('output/make_result.txt', 'r')
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


        run_file = open("output/run_result.txt", 'w')
        if program_type=="freplace/print":
            subprocess.call('./output/freplace', stderr = run_file, shell=False)
        else:
            subprocess.call('./output/test', stderr = run_file, shell=False)
        run_file.close()

        run_file = open("output/run_result.txt", "r")
        run_result = run_file.read().replace('\n', '')
        if 'unknown func' in run_result:
            result_file.write(f"{'no'}\n")
        else:
            result_file.write(f"{'yes'}\n")
        run_file.close()

        

result_file.close()
