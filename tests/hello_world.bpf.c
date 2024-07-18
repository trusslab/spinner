// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2020 Facebook */
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";


SEC("perf_event")
int hello_world(void *ctx)
{
	bpf_printk("hello_world\n");
        return 0;
}

