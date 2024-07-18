#include "vmlinux.h"
#include <errno.h>
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "trie_perf.h"

#define MAX_ENTRIES 1000
#define MAX_NR_CPUS 1024
#define TASK_COMM_LEN 16
#define MAX_FILENAME_LEN 512    
/*
struct {
        __uint(type, BPF_MAP_TYPE_ARRAY);
        //__uint(key_size, sizeof(int));
        //__uint(value_size, sizeof(int));
        __type(key, u32);
        __type(value, long);
        __uint(max_entries, MAX_ENTRIES);
} pb SEC(".maps");
*/

struct {
        __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
        __uint(max_entries, 1);
        __type(key, int);
        __type(value, struct event);
} heap SEC(".maps");

struct ipv4_lpm_key;

struct {
	__uint(type, BPF_MAP_TYPE_LPM_TRIE);
        __type(key, struct ipv4_lpm_key);
        __type(value, __u32);
        __uint(map_flags, BPF_F_NO_PREALLOC);
        __uint(max_entries, 255);
} pb SEC(".maps");

SEC("perf_event")
int trie_perf(void *ctx)
{
        
        struct ipv4_lpm_key key = { 1, 2};
        long init_val = 1;
        long *value;
        int i;
        
        bpf_map_update_elem(&pb, &key, &init_val, BPF_ANY);
	
        for (i = 0; i < 10; i++) {
                value = bpf_map_lookup_elem(&pb, &key);
                /*
		if (value) 
                {

                        bpf_printk("key: %d \t value: %ld \n ", key, value);
                        value=value+1;  
                        //bpf_map_update_elem(&pb, &key, &value, BPF_EXIST);
                }
                */
                if (value)
                        bpf_map_delete_elem(&pb, &key);
                
        }
        
        /*
        struct event *e = {0};
        int zero = 0;

        
        

        e = bpf_map_lookup_elem(&heap, &zero);
        if (!e) 
                return 0;

	e->pid = bpf_get_current_pid_tgid() >> 32;
        bpf_get_current_comm(&e->comm, sizeof(e->comm));
        char *filename = "filename";
        if (e->pid == 0) 
                filename = "my process";

        bpf_probe_read_str(&e->filename, sizeof(e->filename),filename);
        */
        //bpf_perf_event_output(ctx, &pb, BPF_F_CURRENT_CPU, e, sizeof(*e));
        //bpf_map_update_elem(&pb, &key, &value, BPF_ANY);
        bpf_printk("BPF triggered.");
        return 0;
}


char _license[] SEC("license") = "GPL";

