#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    struct bpf_object *obj;
    int prog_fd, err;

    // Open the BPF object file
    obj = bpf_object__open_file("context_test.bpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Error opening BPF object file\n");
        return 1;
    }

    // Load the BPF object into the kernel
    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Error loading BPF object\n");
        return 1;
    }

    // Find the BPF program by name
    struct bpf_program *prog = bpf_object__find_program_by_title(obj, "count_packets");
    if (!prog) {
        fprintf(stderr, "Error finding BPF program by title\n");
        return 1;
    }

    // Get the file descriptor for the BPF program
    prog_fd = bpf_program__fd(prog);
    if (prog_fd < 0) {
        fprintf(stderr, "Error getting BPF program file descriptor\n");
        return 1;
    }

    printf("BPF Program FD: %d\n", prog_fd);

    // Clean up
    bpf_object__close(obj);
    return 0;
}
