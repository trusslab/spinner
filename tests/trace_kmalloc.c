// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
/* Copyright (c) 2020 Facebook */
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <stdbool.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <execinfo.h>
#include <signal.h>
//#include <linux/nsproxy.h>
#include "trace_kmalloc.skel.h"
#include "trace_kmalloc.h"

struct nsproxy *ns;
FILE *f;

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
        return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;

static void sig_handler(int sig)
{
	exiting = true;
}

static int handle_event(void *ctx, void *data, size_t data_sz) 
{

	//f = fopen("trace_results.txt", "a");
	const struct trace_t *t=data;
	//printf("%-7d %-7d %-7d %-7d %-12u", t->pid, t->tgid, t->uid, t->gid, t->upid);
	fprintf(f,"PID: %d\n", t->pid);
	fprintf(f,"TGID: %d\n", t->tgid);
	fprintf(f,"UID: %d\n", t->uid); 
	fprintf(f,"UID: %d\n\n", t->gid);

	fprintf(f,"kmalloc details\n");
	fprintf(f,"call_site: %p\n", t->kd.call_site);
	fprintf(f,"ptr: %p\n", t->kd.ptr);
	fprintf(f,"bytes_req: %ld\n", t->kd.bytes_req);
	fprintf(f,"bytes_alloc: %ld\n", t->kd.bytes_alloc);
	fprintf(f,"gfp_flags: %ld\n", t->kd.gfp_flags);
	fprintf(f,"node: %d\n\n", t->kd.node);
	
	fprintf(f,"uts_namespace details\n");
	fprintf(f,"sysname: %s\n", (char*)t->utsname.sysname);
	fprintf(f,"nodename: %s\n", (char*)t->utsname.nodename);
	fprintf(f,"release: %s\n", (char*)t->utsname.release);
	fprintf(f,"version: %s\n", (char*)t->utsname.version);
	fprintf(f,"machine: %s\n", (char*)t->utsname.machine);
	fprintf(f,"domainname: %s\n\n", (char*)t->utsname.domainname);

	fprintf(f, "mnt_namespace details\n");
	fprintf(f, "seq: %d\n", t->mns.seq);
	fprintf(f, "event: %d\n", t->mns.event);
	fprintf(f, "nr_mounts: %d\n", t->mns.nr_mounts);
	fprintf(f, "pending mounts: %d\n\n", t->mns.pending_mounts);
	
	fprintf(f,"pid_namespace details\n");
	fprintf(f,"idr_base: %d\n", t->pns.idr_base);
	fprintf(f,"idr_next: %d\n", t->pns.idr_next);
	fprintf(f,"pid_allocated: %d\n", t->pns.pid_allocated);
	fprintf(f,"level: %d\n", t->pns.level);
	fprintf(f,"reboot: %d\n\n", t->pns.reboot);

	fprintf(f,"ipc_namespace_details\n");
	fprintf(f,"used_sems: %d\n", t->ins.used_sems);
	fprintf(f,"msg_ctlmax: %d\n", t->ins.msg_ctlmax);
        fprintf(f,"msg_ctlmnb: %d\n", t->ins.msg_ctlmnb);
        fprintf(f,"msg_ctlmni: %d\n", t->ins.msg_ctlmni);
        fprintf(f,"shm_ctlmax: %d\n", t->ins.shm_ctlmax);
	fprintf(f,"shm_ctlall: %d\n", t->ins.shm_ctlall);
        fprintf(f,"shm_tot: %ld\n", t->ins.shm_tot);
        fprintf(f,"shm_ctlmni: %d\n", t->ins.shm_ctlmni);
        fprintf(f,"shm_rmid_forced: %d\n", t->ins.shm_rmid_forced);
        fprintf(f,"mq_queues_count: %d\n", t->ins.mq_queues_count);
	fprintf(f,"mq_queues_max: %d\n", t->ins.mq_queues_max);
        fprintf(f,"mq_msg_max: %d\n", t->ins.mq_msg_max);
	fprintf(f,"mq_msgsize_max: %d\n", t->ins.mq_msgsize_max);
	fprintf(f,"mq_msg_default: %d\n", t->ins.mq_msg_default);

		
	char **strings = backtrace_symbols(t->kstack, t->kstack_sz);
	if (strings!=NULL)
	{	
		fprintf(f,"Stacktrace: \n");
		for (int i=0; i<t->kstack_sz ; i++)
		{	
			if (strcmp(strings[i],"[(nil)]")==0)
				break;
			fprintf(f,"%-10s",strings[i]);
		}
	}
	free(strings);
	fprintf(f,"\n\n");
	return 0;
}

int main(int argc, char **argv)
{	
	struct ring_buffer *events = NULL;
        struct trace_kmalloc_bpf *skel;
        int err;
	f = fopen("trace_kmalloc_results.txt", "a");
	
        /* Set up libbpf errors and debug info callback */
        libbpf_set_print(libbpf_print_fn);
	
	//handling ctrl+c
	signal(SIGINT, sig_handler);
	signal(SIGTERM, sig_handler);

        /* Open BPF application */
        skel = trace_kmalloc_bpf__open();
        if (!skel) {
                fprintf(stderr, "Failed to open BPF skeleton\n");
                return 1;
        }

        /* Load & verify BPF programs */
        err = trace_kmalloc_bpf__load(skel);
        if (err) {
                fprintf(stderr, "Failed to load and verify BPF skeleton\n");
                goto cleanup;
        }

        /* Attach tracepoint handler */
        err = trace_kmalloc_bpf__attach(skel);
        if (err) {
                fprintf(stderr, "Failed to attach BPF skeleton\n");
                goto cleanup;
        }
	
	/* Set up ring buffer polling */
	events = ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, NULL, NULL);
	if (!events) {
		err = -1;
		fprintf(stderr, "Failed to create ring buffer\n");
		goto cleanup;
	}

        printf("Successfully started!\n");
	
	//printf("%-7s %-7s %-7s %-7s %-12s %-16s\n", "PID", "TGID", "UID", "GID", "PID Alloc", "Stack Trace");
	
        while(!exiting) {
                /* trigger our BPF program */
                //fprintf(stderr, ".");
                //sleep(1);
		err = ring_buffer__poll(events, 100 /* timeout, ms */);

		/* Ctrl-C will cause -EINTR */
		if (err == -EINTR) {
			err = 0;
			break;
		}
		if (err < 0) {
			printf("Error polling perf buffer: %d\n", err);
			break;
		}
        }

cleanup:
	fclose(f);
        trace_kmalloc_bpf__destroy(skel);
        return -err;
}

