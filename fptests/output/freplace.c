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
#include <bpf/btf.h>
#include <execinfo.h>
#include <signal.h>



static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
        return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;

static void sig_handler(int sig)
{
        exiting = true;
}

int main(int argc, char **argv)
{
	int err, tgt_fd;
        /* Set up libbpf errors and debug info callback */
        libbpf_set_print(libbpf_print_fn);

        //handling ctrl+c
        signal(SIGINT, sig_handler);
        signal(SIGTERM, sig_handler);
	
	const char *obj_file = "output/test.bpf.o";
	const char *target_obj_file = "output/freplace2.bpf.o";
	
	struct bpf_object *obj = bpf_object__open_file(obj_file, NULL);
	if (!obj) 
		return 1;

	struct bpf_object *tgt_obj = bpf_object__open_file(target_obj_file, NULL);
	if(!tgt_obj)
		return 1;

	struct btf *btf = bpf_object__btf(tgt_obj);

	err = bpf_object__load(tgt_obj);
	if (err) {
		fprintf(stderr, "Error loading BPF target object\n");
		return 1;
	}

	// Find the BPF program by name
	struct bpf_program *prog = bpf_object__find_program_by_name(tgt_obj, "freplace_test");
        if (!prog) {
                fprintf(stderr, "Error finding BPF program by title\n");
                return 1;
        }

	struct bpf_program *p = bpf_object__find_program_by_name(obj, "test_prog");
	if (!p) {
		fprintf(stderr, "Error finding BPF program by title\n");
		return 1;
	}

	struct bpf_link *link_target = bpf_program__attach(prog);
        if (!link_target) {
                fprintf(stderr, "Error autoattaching target program\n");
                return 1;
        }


	// Get the file descriptor for the BPF program
	tgt_fd = bpf_program__fd(prog);
	if (tgt_fd < 0) {
		fprintf(stderr, "Error getting BPF program file descriptor\n");
		return 1;
	}
	

	err= bpf_program__set_attach_target(p, tgt_fd, "print");
	if (err) {
		fprintf(stderr, "Error setting attach target\n");
		return 1;
	}

	err = bpf_object__load(obj);
        if (err) {
                fprintf(stderr, "Error loading BPF target object\n");
                return 1;
        }

	
	struct bpf_link *link = bpf_program__attach(p);
	if (!link) {
		fprintf(stderr, "Error autoattaching replacement program\n");
		return 1;
	}	

	printf("successful");
	//while(!exiting) {}
	return 0;

}
