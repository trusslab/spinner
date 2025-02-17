#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <stdbool.h>
#include <sys/resource.h>
#include <linux/bpf.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
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
        int err;

        libbpf_set_print(libbpf_print_fn);

        //handling ctrl+c
        signal(SIGINT, sig_handler);
        signal(SIGTERM, sig_handler);


        const char *obj_file1 = "poc.bpf.o";
        struct bpf_object *obj1 = bpf_object__open_file(obj_file1, NULL);
        if (!obj1)
                return 1;


        err = bpf_object__load(obj1);
        if (err) {
                fprintf(stderr, "Error loading BPF target object\n");
                return 1;
        }

        struct bpf_program *prog1 = bpf_object__find_program_by_name(obj1, "test_prog1");
        if (!prog1) {
                fprintf(stderr, "Error finding BPF program by title\n");
                goto cleanup;
        }

        //LIBBPF_OPTS(bpf_test_run_opts, opts);
        //int ret = bpf_prog_test_run_opts(bpf_program__fd(prog1), &opts);


        struct bpf_program *prog2 = bpf_object__find_program_by_name(obj1, "test_prog2");
        if (!prog2) {
                fprintf(stderr, "Error finding BPF program by title\n");
                goto cleanup;
        }


        struct bpf_link *link1 = bpf_program__attach(prog1);
        if (!link1) {
                fprintf(stderr, "Error attaching prog1\n");
                goto cleanup;
        }


        struct bpf_link *link2 = bpf_program__attach(prog2);
        if (!link2) {
                fprintf(stderr, "Error attaching kprobe\n");
                goto cleanup;
        }


        printf("Started successfully");

        while(!exiting) {
        }
        bpf_link__destroy(link1);
        bpf_link__destroy(link2);



cleanup:

        bpf_object__close(obj1);
        return 0;

}


