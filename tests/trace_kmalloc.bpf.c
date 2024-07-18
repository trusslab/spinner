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
#include "trace_kmalloc.h"


char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
        __uint(type, BPF_MAP_TYPE_RINGBUF);
        __uint(max_entries, 256 * 1024);
} events SEC(".maps");

SEC("tp/kmem/kmalloc")
int handle_tp(struct trace_event_raw_kmalloc *ctx)
{	
	__u32 pid = bpf_get_current_pid_tgid();
        __u32 tgid = bpf_get_current_pid_tgid() >> 32;

        __u32 uid = bpf_get_current_uid_gid();
        __u32 gid = bpf_get_current_uid_gid() >> 32;
	
	struct trace_t *event;
	

        event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
	if (!event) {
		return 0;
	}

	event->pid = pid;
	event->tgid = tgid;
	event->uid = uid;
	event->gid = gid;
	/*
        bpf_printk("PID: %d", pid);
        bpf_printk("TGID: %d", tgid);
        bpf_printk("UID: %d", uid);
        bpf_printk("GID: %d", gid);
	*/
	
	event->kd.bytes_alloc = ctx->bytes_alloc;
	event->kd.call_site = ctx->call_site;
	event->kd.ptr = ctx->ptr;
	event->kd.bytes_req = ctx->bytes_req;
	event->kd.gfp_flags = ctx->gfp_flags;
	event->kd.node = ctx->node;


	if (bpf_get_current_comm(event->comm, sizeof(event->comm)))
                event->comm[0] = 0;

        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
	//Reading uts_namespace
	//Reading new_utsname
	struct nsproxy *ns;
	BPF_CORE_READ_INTO(&event->ns, task, nsproxy);

	BPF_CORE_READ_INTO(event->utsname.sysname, task, nsproxy, uts_ns, name.sysname);;
	BPF_CORE_READ_INTO(event->utsname.nodename, task, nsproxy, uts_ns, name.nodename);
	BPF_CORE_READ_INTO(event->utsname.release, task, nsproxy, uts_ns, name.release);
	BPF_CORE_READ_INTO(event->utsname.version, task, nsproxy, uts_ns, name.version);
	BPF_CORE_READ_INTO(event->utsname.machine, task, nsproxy, uts_ns, name.machine);
	BPF_CORE_READ_INTO(event->utsname.domainname, task, nsproxy, uts_ns, name.domainname);

	//Reading mnt namespace
	event->mns.seq = BPF_CORE_READ(task, nsproxy, mnt_ns, seq);
	event->mns.event = BPF_CORE_READ(task, nsproxy, mnt_ns, event);
 	//event->mns.nr_mounts = BPF_CORE_READ(task, nsproxy, mnt_ns, mounts);
        event->mns.pending_mounts = BPF_CORE_READ(task, nsproxy, mnt_ns, pending_mounts);

	//Reading pid namespace	
	event->pns.idr_base = BPF_CORE_READ( task, nsproxy, pid_ns_for_children, idr.idr_base);
	event->pns.idr_next = BPF_CORE_READ( task, nsproxy, pid_ns_for_children, idr.idr_next);
 	event->pns.pid_allocated = BPF_CORE_READ( task, nsproxy, pid_ns_for_children, pid_allocated);
	event->pns.level = BPF_CORE_READ( task, nsproxy, pid_ns_for_children, level);
	event->pns.reboot = BPF_CORE_READ( task, nsproxy, pid_ns_for_children, reboot);

	//reading ipc namespace
	BPF_CORE_READ_INTO(event ->ins.sem_ctls, task, nsproxy, ipc_ns, sem_ctls);
	event ->ins.used_sems = BPF_CORE_READ(task, nsproxy, ipc_ns, used_sems);
	event ->ins.msg_ctlmax = BPF_CORE_READ(task, nsproxy, ipc_ns, msg_ctlmax);
	event ->ins.msg_ctlmnb = BPF_CORE_READ(task, nsproxy, ipc_ns, msg_ctlmnb);
	event ->ins.msg_ctlmni = BPF_CORE_READ(task, nsproxy, ipc_ns, msg_ctlmni);
	event ->ins.shm_ctlmax = BPF_CORE_READ(task, nsproxy, ipc_ns, shm_ctlmax);
	event ->ins.shm_ctlall = BPF_CORE_READ(task, nsproxy, ipc_ns, shm_ctlall);
	event ->ins.shm_tot = BPF_CORE_READ(task, nsproxy, ipc_ns, shm_tot);
	event ->ins.shm_ctlmni = BPF_CORE_READ(task, nsproxy, ipc_ns, shm_ctlmni);
	event ->ins.shm_rmid_forced = BPF_CORE_READ(task, nsproxy, ipc_ns, shm_rmid_forced);
	event ->ins.mq_queues_max = BPF_CORE_READ(task, nsproxy, ipc_ns, mq_queues_max);

	event->kstack_sz = bpf_get_stack(ctx, event->kstack, sizeof(event->kstack), 0);
	event->ustack_sz = bpf_get_stack(ctx, event->ustack, sizeof(event->ustack), BPF_F_USER_STACK);

	
//	struct linux_binprm *arg = (struct linux_binprm *) PT_REGS_PARM1(ctx);
        bpf_ringbuf_submit(event, 0);

        return 0;
}

