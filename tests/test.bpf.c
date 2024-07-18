#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
        __uint(type, BPF_MAP_TYPE_SOCKMAP);
        __uint(max_entries, 1);
        __type(key, __u32);
        __type(value, __u64);
} this_map SEC(".maps");

SEC("fmod_ret/bpf_modify_return_test")
int test_prog(void *ctx){
        __u32 v0 = 0;
        __u64 v1 = 0;
        v1 = bpf_map_delete_elem(&this_map, &v0);
        bpf_printk("bpf triggered");
return 0;
}

