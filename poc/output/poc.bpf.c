#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
__uint(type, BPF_MAP_TYPE_HASH);
__type(key, int);
__type(value,int);
__uint(max_entries, 25);
} this_map SEC(".maps");

SEC("kprobe/my_nmi_handler")
int test_prog1(void *ctx){
int key = 686;
int value = 481;
 u64 flags = 10;

long ret = bpf_map_update_elem(&this_map, &key, &value, flags);
bpf_printk("bpf_prog 1");
return 0;
}SEC("fentry/do_nanosleep")
int test_prog2(void *ctx){
int key = 699;
int value = 473;
 u64 flags = 1;

long ret = bpf_map_update_elem(&this_map, &key, &value, flags);
bpf_printk("bpf_prog 2");
return 0;
}