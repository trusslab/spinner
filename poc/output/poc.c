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
#include <fcntl.h>

#define DEBUGFS_TRIGGER_PATH "/sys/kernel/debug/example_nmi_handler/trigger_nmi"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args) {
	return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;
static void sig_handler(int sig) {
	exiting = true;
}

int main(int argc, char **argv)
{
int err;
libbpf_set_print(libbpf_print_fn);

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
	fprintf(stderr, "Error finding BPF program 1 by title\n");
	goto cleanup;
}

struct bpf_program *prog2 = bpf_object__find_program_by_name(obj1, "test_prog2");
if (!prog2) {
	fprintf(stderr, "Error finding BPF program 2 by title\n");
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

int fd;
const char *data = "1";
ssize_t bytes_written;

fd = open(DEBUGFS_TRIGGER_PATH, O_WRONLY);
if (fd < 0) {
	perror("Failed to open trigger file");
}

bytes_written = write(fd, data, sizeof(data));
if (bytes_written < 0) {
	perror("Failed to write to trigger file");
	close(fd);
}

printf("Successfully triggered NMI handler.");

if (fd)
	close(fd);

printf("Started successfully");
int i;
for (i=0; i<4; i+=1) { sleep(3); }
bpf_link__destroy(link1);
bpf_link__destroy(link2);

cleanup:
bpf_object__close(obj1);
return 0;
}

