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
#include "test.skel.h"



static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
        return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;

static void sig_handler(int sig)
{
	exiting = true;
}

/*
static int handle_event(void *ctx, void *data, size_t data_sz) 
{

	return 0;	
}
*/

int main(int argc, char **argv)
{	
        struct test_bpf *skel;
        int err;
	
        /* Set up libbpf errors and debug info callback */
        libbpf_set_print(libbpf_print_fn);
	
	//handling ctrl+c
	signal(SIGINT, sig_handler);
	signal(SIGTERM, sig_handler);

        /* Open BPF application */
        skel = test_bpf__open();
        if (!skel) {
                fprintf(stderr, "Failed to open BPF skeleton\n");
                return 1;
        }

        /* Load & verify BPF programs */
        err = test_bpf__load(skel);
        if (err) {
                fprintf(stderr, "Failed to load and verify BPF skeleton\n");
                goto cleanup;
        }

        /* Attach tracepoint handler */
        err = test_bpf__attach(skel);
        if (err) {
                fprintf(stderr, "Failed to attach BPF skeleton\n");
                goto cleanup;
        }
	

        printf("Successfully started!\n");

	//while (!exiting) {}	
	

cleanup:
        test_bpf__destroy(skel);
        return -err;
}

