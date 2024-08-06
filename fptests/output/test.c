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



static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
        return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;

int main(int argc, char **argv)
{	
        struct test_bpf *skel;
        int err;
	
        /* Set up libbpf errors and debug info callback */
        libbpf_set_print(libbpf_print_fn);
	
	const char *obj_file = "output/test.bpf.o";
	struct bpf_object *obj = bpf_object__open_file(obj_file, NULL);
	if (!obj)
		return 1;

	err = bpf_object__load(obj);
	if (err) {
		fprintf(stderr, "Error loading BPF target object\n");
		return 1;
	}
	
	struct bpf_program *prog = bpf_object__find_program_by_name(obj, "test_prog");
	if (!prog) {
		fprintf(stderr, "Error finding BPF program by title\n");
		goto cleanup;
	}


	struct bpf_link *link = bpf_program__attach(prog);
        if (!link) {
                fprintf(stderr, "Error attaching to print_address_i8\n");
                return 1;
        }

	printf("Started successfully");
	bpf_link__destroy(link);
cleanup:
	bpf_object__close(obj);
	return 0;

}

