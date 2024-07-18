//#include "vmlinux.h"
#include <linux/version.h>
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("fentry/do_nanosleep")
int test_prog(void *ctx){
bpf_printk("hello");
return 0;
}
