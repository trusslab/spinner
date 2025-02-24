import subprocess

# Define the command to run GDB and execute your script
def disassemble_function(function):
    gdb_command = [
        "gdb",
        "/home/priya/s2e/images/debian-12.5-x86_64/guestfs/vmlinux",
        "--batch",  # Run GDB in batch mode
        "-ex", f"disassemble {function}",  # Your command(s)
        "-ex", "quit"  # Quit GDB when done
    ]

    # Run the command and capture the output
    result = subprocess.run(gdb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode("utf-8")

    return output

def find_attach(function, program_type, lock_type):
    if program_type == 'tracepoint':
        return "lock/lock_acquired"
    
    elif program_type == 'kprobe':
        disassembled = disassemble_function(function)
        instrs = disassembled.split('\n')
        for i in range(len(instrs)):
            if lock_type in instrs[i]:
                offset_expression = instrs[i+1].split()[1]
                offset = offset_expression[offset_expression.index('<')+2:offset_expression.index('>')]
                return function+"+"+offset
        return 'none'

    elif program_type == 'fentry':
        disassembled = disassemble_function(function)
        instrs = disassembled.split('\n')
        lock_dict ={'_raw_spin_lock_irqsave': '_raw_spin_unlock_irqrestore', 
                '_raw_spin_lock_irq' : '_raw_spin_unlock_irq', 
                '_raw_spin_lock_bh': '_raw_spin_unlock_bh', 
                '_raw_spin_lock': '_raw_spin_unlock'}
        start_read = False
        for i in range(len(instrs)):
            if lock_type in instrs[i]:
                start_read = True
                continue
            if start_read and lock_dict[lock_type] in instrs[i]:
                return 'none'
            if start_read:
                instr_split = instrs[i].split()
                if instr_split[2] == 'call':
                    attach_function = instr_split[-1][1:-1]
                    return attach_function
        return 'none'
    else:
        return "not matching prog type"

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


def convert_prog_type(prog_type):
    if prog_type=="BPF_PROG_TYPE_TRACING":
        return ["fmod_ret", "fmod_ret.s", "fentry", "fentry.s", "fexit", "fexit.s", "freplace", "iter", "iter.s", "tp_btf"]
    if prog_type=="BPF_PROG_TYPE_SYSCALL":
        return ['syscall']
    if prog_type=="BPF_PROG_TYPE_LSM":
        return ["lsm_cgroup", "lsm", "lsm.s"]
    if prog_type=="BPF_PROG_TYPE_UNSPEC":
        return ["cgroup/dev", "cgroup/skb", "cgroup_skb/egress", "cgroup_skb/ingress", "cgroup/getsockopt", "cgroup/setsockopt", "cgroup/bind4", 
                "cgroup/bind6", "cgroup/connect4", "cgroup/connect6", "cgroup/getpeername4", "cgroup/getpeername6", "cgroup/getsockname4", 
                "cgroup/getsockname6", "cgroup/recvmsg4", "cgroup/sendmsg4", "cgroup/recvmsg6", "cgroup/sendmsg6", "cgroup/connect_unix", 
                "cgroup/sendmsg_unix", "cgroup/recvmsg_unix", "cgroup/getpeername_unix", "cgroup/getsockname_unix", "cgroup/post_bind4", 
                "cgroup/post_bind6", "cgroup/sock_create", "cgroup/sock", "cgroup/sock_release", "cgroup/sysctl", "flow_dissector", "kprobe", 
                "kretprobe", "ksyscall", "kretsyscall", "uprobe", "uprobe.s", "uretprobe", "uretprobe.s", "usdt", "kprobe.multi", "kretprobe.multi", 
                "lirc_mode2", "lsm_cgroup", "lsm", "lsm.s", "lwt_in", "lwt_out", "lwt_seg6local", "lwt_xmit", "perf_event", "raw_tp.w", 
                "raw_tracepoint.w", "raw_tp", "raw_tracepoint", "action", "classifier", "tc", "sk_lookup", "sk_msg", "sk_reuseport/migrate", 
                "sk_reuseport", "sk_skb", "sk_skb/stream_parser", "sk_skb/stream_verdict", "socket", "sockops", "syscall", "tp", "tracepoint", 
                "fmod_ret", "fmod_ret.s", "fentry", "fentry.s", "fexit", "fexit.s", "freplace", "iter", "iter.s", "tp_btf", "xdp.frags/cpumap", 
                "xdp/cpumap", "xdp.frags/devmap", "xdp/devmap", "xdp", "xdp.frags", "struct_ops"]
    if prog_type=="BPF_PROG_TYPE_STRUCT_OPS":
        return ['struct_ops']
    if prog_type=="BPF_PROG_TYPE_SCHED_CLS":
        return ['classifier', 'tc']
    if prog_type=="BPF_PROG_TYPE_XDP":
        return ["xdp", "xdp.frags/cpumap", "xdp/cpumap", "xdp.frags/devmap", "xdp/devmap", "xdp.frags"]
    if prog_type=="BPF_PROG_TYPE_SCHED_ACT":
        return ['action']
    if prog_type=="BPF_PROG_TYPE_CGROUP_SOCK_ADDR":
        return ['cgroup/bind4', 'cgroup/bind6', 'cgroup/connect4', 'cgroup/connect6', 'cgroup/getpeername4', 'cgroup/getpeername6', 
                'cgroup/getsockname4', 'cgroup/getsockname6', 'cgroup/recvmsg4', 'cgroup/sendmsg4', 'cgroup/recvmsg6', 'cgroup/sendmsg6', 
                'cgroup/connect_unix', 'cgroup/sendmsg_unix', 'cgroup/recvmsg_unix', 'cgroup/getpeername_unix', 'cgroup/getsockname_unix']

def complete_attach(prog_type):
    if prog_type == "tp":
        return 'tp/sched/sched_switch'
    if prog_type == "tracepoint":
        return 'tracepoint/sched/sched_switch'
    
    if prog_type == "fmod_ret":
        return 'fmod_ret/bpf_modify_return_test'
    if prog_type == "fmod_ret.s":
        return 'fmod_ret.s/bpf_fentry_test1'
    if prog_type == "fentry":
        return 'fentry/do_nanosleep'
    if prog_type == "fentry.s":
        return 'fentry.s/bpf_fentry_test1'
    if prog_type == "fexit":
        return 'fexit/do_nanosleep'
    if prog_type == "fexit.s":
        return 'fexit.s/bpf_fentry_test1'
    if prog_type == "freplace":
        return 'freplace/print' #requires additional modification to POC 
    if prog_type == "iter":
        return 'iter/tcp'
    if prog_type == "iter.s":
        return 'iter.s/cgroup'
    if prog_type == "tp_btf":
        return 'tp_btf/task_newtask'

    if prog_type == "lsm_cgroup":
        return 'lsm_cgroup/socket_bind'
    if prog_type == 'lsm':
        return 'lsm/task_free'
    if prog_type == 'lsm.s':
        return 'lsm.s/bpf'

    if prog_type == 'kprobe':
        return 'kprobe/do_nanosleep'
    if prog_type == 'kretprobe':
        return 'kretprobe/do_nanosleep'
    if prog_type == 'ksyscall':
        return 'ksyscall/getgid'
    if prog_type == 'kretsyscall':
        return 'kretsyscall/getgid',
    if prog_type == 'uprobe':
        return 'uprobe/output/test:libbpf_print_fn'
    if prog_type == 'uprobe.s':
        return 'uprobe.s/output/test:libbpf_print_fn'
    if prog_type == 'uretprobe':
        return 'uretprobe/output/test:libbpf_print_fn'
    if prog_type == 'uretprobe.s':
        return 'uretprobe.s/output/test:libbpf_print_fn', 
    if prog_type == 'usdt':
        return 'usdt/libc.so.6:libc:setjmp'
    if prog_type == 'kprobe.multi':
        return 'kprobe.multi/*_nanosleep'
    if prog_type == 'kretprobe.multi':
        return 'kretprobe.multi/*_nanosleep'

    return prog_type

if __name__=='__main__':
    print(find_attach('percpu_counter_add_batch', 'kprobe', '_raw_spin_lock'))
