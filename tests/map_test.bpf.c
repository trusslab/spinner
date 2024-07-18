#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
struct {
__uint(type, BPF_MAP_TYPE_CGROUP_STORAGE);
__uint(max_entries, 1);
__type(key, struct bpf_cgroup_storage_key);
__type(value, __u64);
} this_map SEC(".maps");

SEC("cgroup_skb/ingress")
int test_prog(void *ctx){
__u32 v0 = 0;
__u64 v1 = 0;
bpf_printk("hello");
return 0;
}
