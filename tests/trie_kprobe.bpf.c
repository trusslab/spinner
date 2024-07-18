// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2021 Sartura */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "trie_perf.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

#define MAX_ENTRIES 1000
#define MAX_NR_CPUS 1024
#define TASK_COMM_LEN 16
#define MAX_FILENAME_LEN 512

struct ipv4_lpm_key;

struct {
        __uint(type, BPF_MAP_TYPE_LPM_TRIE);
        __type(key, struct ipv4_lpm_key);
        __type(value, __u32);
        __uint(map_flags, BPF_F_NO_PREALLOC);
        __uint(max_entries, 255);
} pb SEC(".maps");

SEC("ksyscall/clone")
int BPF_KPROBE(do_unlinkat, int dfd, struct filename *name)
{

        struct ipv4_lpm_key key = { 1, 2};
        long init_val = 1;
        long *value;
        int i;

        bpf_map_update_elem(&pb, &key, &init_val, BPF_ANY);

        for (i = 0; i < 10; i++) {
                value = bpf_map_lookup_elem(&pb, &key);
		if (value)
                        bpf_map_delete_elem(&pb, &key);

        }
	 bpf_printk("BPF triggered in process context.");
        return 0;
}


char _license[] SEC("license") = "GPL";


