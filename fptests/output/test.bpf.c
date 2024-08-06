#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("cgroup/dev")
int test_prog(void *ctx){
struct sk_buff * param0;
u32  param1;
long ret = bpf_skb_change_type( param0, param1);
return 0;
}
