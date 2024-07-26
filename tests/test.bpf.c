#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("cgroup/connect_unix")
int test_prog(void *ctx){
u64 ret = bpf_get_current_pid_tgid();
return 0;
}
