#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include <usdt.bpf.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("cgroup/getsockname6")
int test_prog(void *ctx){
void * param0;
u64  param1;
bpf_ringbuf_discard( param0, param1);
return 0;
}
