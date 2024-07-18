// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2020 Facebook */
//#include <linux/bpf.h>
//#include <linux/types.h>
//#include <bpf/bpf_helpers.h>
//#include <linux/sched.h>
#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
//#include <string.h>
#define ARENA_SIZE (1ull << 32)
#define PAGE_SIZE __PAGE_SIZE

//extern void *bpf_arena_alloc_pages(void *p__map, void *addr__ign, u32 page_cnt, int node_id, u64 flags) __ksym;
extern void bpf_rcu_read_lock(void) __ksym;
extern void bpf_rcu_read_unlock(void) __ksym;
extern void cgroup_rstat_flush(struct cgroup *cgrp) __ksym;

char LICENSE[] SEC("license") = "Dual BSD/GPL";
/*
struct {
	__uint(type, BPF_MAP_TYPE_ARENA);
	__uint(map_flags, BPF_F_MMAPABLE);
	__uint(max_entries, ARENA_SIZE / PAGE_SIZE);
} arena SEC(".maps");
*/
SEC("tp_btf/sched_switch")
int arena_prog(void *ctx)
{	
	//volatile int __arena *page1;	
	/*
	bpf_rcu_read_lock();
	bpf_rcu_read_unlock();
	*/
	struct cgroup *cgrp ;
	cgroup_rstat_flush(cgrp);

	bpf_printk("bpf triggered");
        return 0;
}

