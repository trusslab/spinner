#include <linux/perf_event.h>


static volatile bool exiting = false;

static void sig_handler(int sig)
{
        exiting = true;
        return;
}
extern int parse_cpu_mask_file(const char *fcpu, bool **mask, int *mask_sz);

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu, int group_fd,
                            unsigned long flags)
{
        int ret;

        ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
        return ret;
}

int main(int argc, char *const argv[])
{
        const char *online_cpus_file = "/sys/devices/system/cpu/online";
	int num_cpus, num_online_cpus;
	bool *online_mask = NULL;

	signal(SIGINT, sig_handler);
        signal(SIGTERM, sig_handler);

        err = parse_cpu_mask_file(online_cpus_file, &online_mask, &num_online_cpus);
        if (err) {
                fprintf(stderr, "Fail to get online CPU numbers: %d\n", err);
                goto cleanup;
        }

        num_cpus = libbpf_num_possible_cpus();
        if (num_cpus <= 0) {
                fprintf(stderr, "Fail to get the number of processors\n");
                err = -1;
                goto cleanup;
        }

	struct perf_event_attr attr;
	attr.type = PERF_TYPE_HARDWARE;
        attr.config = PERF_COUNT_HW_CPU_CYCLES;
        attr.sample_freq = 10;
        attr.inherit = 1;
        attr.freq = 1;

	int pefd = perf_event_open(&attr, pid, cpu, -1, PERF_FLAG_FD_CLOEXEC);
	if (pefd < 0) {
                        fprintf(stderr, "Fail to set up performance monitor on a CPU/Core\n");
                        err = -1;
                        goto cleanup;
        }

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

        struct bpf_program *prog2 = bpf_object__find_program_by_name(obj1, "test_prog2");
        if (!prog2) {
                fprintf(stderr, "Error finding BPF program by title\n");
                goto cleanup;
        }


        struct bpf_link *link1 = bpf_program__attach_perf_event(prog1, pefd);
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
