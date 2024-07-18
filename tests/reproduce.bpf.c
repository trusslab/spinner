
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>


SEC("perf_event")
int func(struct bpf_perf_event_data *ctx) {
        bpf_printk("BPF triggered");
        uint64_t v5 = 1;
        char v0[56] = {};
        uint64_t v6 = bpf_get_current_task();
	uint64_t * var6 = &v6;	

	const void * v7 = var6;
	bpf_printk("v6 is %p", v7);

	long var = (long)v7;
	bpf_printk("var is %ld", var);
	

	/*	
	if (__builtin_constant_p(v5 <= 4096) && v5 <= 4096)
		bpf_printk("condition 1");
	*/
	/*
	unsigned long sum = v5 + (unsigned long)v7;
	bool v8 = (long)sum>=0; //valid address check
	bool v9 = v8 && sum >= (unsigned long)v7;
	
	if (!v9)
		bpf_printk("access okay");
	*/
        
	if (v5 < 56) {
                if(bpf_probe_read_user(v0, v5,&v6))
                        bpf_printk("read failed");
        }
        return 374850;
}
char _license[] SEC("license") = "GPL";



