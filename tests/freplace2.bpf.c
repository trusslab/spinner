//#include "vmlinux.h"
#include <linux/version.h>
#include <linux/types.h>
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
//#include <time.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";

__noinline int print() {
	 bpf_printk("hello original");
	 return 0;
}

SEC("kprobe/do_nanosleep")
int freplace_test(void *ctx){
	int res = print();
	return res;
}
