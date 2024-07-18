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
	int fd = bpf_prog_get_fd_by_id(32);
	struct bpf_object *bpf_obj = bpf_object__open("test.o");
	prog = bpf_object__find_program_by_title(trace_obj,
                                           "fentry/myfunc");
  bpf_program__set_expected_attach_type(prog, BPF_TRACE_FENTRY);
  bpf_program__set_attach_target(prog, xdp_fd,
                                 "xdpfilt_blk_all");
  bpf_object__load(trace_obj)
        printf("Successfully started!\n");

	//while (!exiting) {}	
	

cleanup:
        
        return 0;
}

