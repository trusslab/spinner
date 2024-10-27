import sys
import subprocess
from create_test import create_test
from compile_results import compile_results
from test_struct_ops import test_struct_ops

result_file = open('output/helper-progtype.txt','w')
result_file.write(f"{'function_name':<40}{'program_type':<40}{'compile error':<15}{'compile warning':<15}{'sleepable':<15}{'allowed'}\n")
uapi_file_path = sys.argv[1] + "/include/uapi/linux/bpf.h"

program_types = [ 'cgroup/dev', 'cgroup/skb','cgroup_skb/egress', 'cgroup_skb/ingress', 'cgroup/getsockopt', 'cgroup/setsockopt', 'cgroup/bind4',
        'cgroup/bind6', 'cgroup/connect4', 'cgroup/connect6', 'cgroup/getpeername4', 'cgroup/getpeername6', 'cgroup/getsockname4', 'cgroup/getsockname6', 
        'cgroup/recvmsg4', 'cgroup/sendmsg4', 'cgroup/recvmsg6', 'cgroup/sendmsg6', 'cgroup/connect_unix', 'cgroup/sendmsg_unix', 'cgroup/recvmsg_unix', 
        'cgroup/getpeername_unix', 'cgroup/getsockname_unix', 'cgroup/post_bind4', 'cgroup/post_bind6', 'cgroup/sock_create', 'cgroup/sock', 
        'cgroup/sock_release', 'cgroup/sysctl', 'flow_dissector', 'kprobe/do_nanosleep', 'kretprobe/do_nanosleep', 'ksyscall/getgid', 'kretsyscall/getgid', 
        'uprobe/output/test:libbpf_print_fn', 'uprobe.s/output/test:libbpf_print_fn', 'uretprobe/output/test:libbpf_print_fn', 
        'uretprobe.s/output/test:libbpf_print_fn', 'usdt/libc.so.6:libc:setjmp', 'kprobe.multi/*_nanosleep', 'kretprobe.multi/*_nanosleep', 'lirc_mode2', 
        'lsm_cgroup/socket_bind', 'lsm/task_free', 'lsm.s/bpf', 'lwt_in', 'lwt_out', 'lwt_seg6local', 'lwt_xmit', 'perf_event', 'raw_tp.w/sys_enter', 
        'raw_tracepoint.w/sys_enter', 'raw_tp/sys_enter', 'raw_tracepoint/sys_enter', 'action', 'classifier', 'tc', 'sk_lookup', 'sk_msg', 
        'sk_reuseport/migrate', 'sk_reuseport', 'sk_skb', 'sk_skb/stream_parser', 'sk_skb/stream_verdict', 'socket', 'sockops', 'syscall',
        'tp/sched/sched_switch', 'tracepoint/sched/sched_switch', 'fmod_ret/bpf_modify_return_test', 'fmod_ret.s/bpf_fentry_test1', 'fentry/do_nanosleep', 
        'fentry.s/bpf_fentry_test1', 'fexit/do_nanosleep', 'fexit.s/bpf_fentry_test1', 'freplace/print', 'iter/tcp', 'iter.s/cgroup', 'tp_btf/task_newtask',
        'xdp.frags/cpumap', 'xdp/cpumap', 'xdp.frags/devmap', 'xdp/devmap', 'xdp', 'xdp.frags']

for program_type in program_types:

    marker = "* Start of BPF helper function descriptions:"
    for i in range(216):
        marker = create_test(program_type, marker, uapi_file_path)
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
        dont_strip = ['cgroup', 'cgroup_skb','sk_reuseport', 'sk_skb', 'xdp', 'xdp.frags']
        if written_prog_type.split('/')[0] not in dont_strip:
            written_prog_type = written_prog_type.split('/')[0]
        result_file.write(f"{written_prog_type:<40}")

       
        make_command = ['clang', '-O2', '-g', '-target', 'bpf', '-D__TARGET_ARCH_x86', '-I/usr/include/bpf/', '-c', 'output/test.bpf.c', '-o', 'output/test.bpf.o']
        make_result = subprocess.run(make_command, shell = False, capture_output=True, text=True).stderr
        if program_type == "freplace/print":
            make_command = ['gcc', '-L/usr/lib64/', '-o', 'output/freplace', 'output/freplace.c', '-lbpf']
        else:
            make_command = ['gcc', '-L/usr/lib64/', '-o', 'output/test', 'output/test.c', '-lbpf']
        make_result += subprocess.run(make_command, shell = False, capture_output=True, text=True).stderr
        if 'error' in make_result:
            result_file.write(f"{'yes':<15}")
        else:
            result_file.write(f"{'no':<15}")
        if 'warning' in make_result:
            result_file.write(f"{'yes':<15}")
        else:
            result_file.write(f"{'no':<15}")       


        if program_type=="freplace/print":
            run_result = subprocess.run(["./output/freplace"], shell = False, capture_output=True, text=True).stderr
        else:
            run_result = subprocess.run(["./output/test"], shell = False, capture_output=True, text=True).stderr
        if 'helper call might sleep in a non-sleepable prog' in run_result:
            result_file.write(f"{'yes':15}")
        else:
            result_file.write(f"{'no':15}")

        if 'unknown func' in run_result or 'program of this type cannot use' in run_result or 'helper call might sleep in a non-sleepable prog' in run_result:
            result_file.write(f"{'no'}\n")
        else:
            result_file.write(f"{'yes'}\n")
        

result_file.close()

test_struct_ops(uapi_file_path)
compile_results()
