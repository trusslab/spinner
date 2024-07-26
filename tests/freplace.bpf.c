//#include "vmlinux.h"
#include <linux/version.h>
#include <linux/types.h>
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <time.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";



SEC("freplace/print")
__noinline int freplace_test_new(){
	bpf_printk("hello new");
	return 0 ;
}
