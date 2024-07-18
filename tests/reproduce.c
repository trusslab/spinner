#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/sysinfo.h>
#include <linux/perf_event.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <sys/resource.h>
#include "reproduce.skel.h"
#include "reproduce.h"

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
        int freq = 1, pid = -1, cpu;
        struct reproduce_bpf *skel = NULL;
        struct perf_event_attr attr;
        struct bpf_link **links = NULL;
        int num_cpus, num_online_cpus;
        int *pefds = NULL, pefd;
        int argp, i, err = 0;
        bool *online_mask = NULL;

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

        skel = reproduce_bpf__open_and_load();
        if (!skel) {
                fprintf(stderr, "Fail to open and load BPF skeleton\n");
                err = -1;
                goto cleanup;
        }

        pefds = malloc(num_cpus * sizeof(int));
        for (i = 0; i < num_cpus; i++) {
                pefds[i] = -1;
        }

links = calloc(num_cpus, sizeof(struct bpf_link *));

        memset(&attr, 0, sizeof(attr));

        attr.type= PERF_TYPE_SOFTWARE;
        //attr.size = sizeof(attr);
        attr.config = PERF_COUNT_SW_CPU_CLOCK;
        attr.sample_freq = 50;
        attr.inherit = 1;
        attr.freq = 1;




        for (cpu = 0; cpu < num_cpus; cpu++) {
                /* skip offline/not present CPUs */
                if (cpu >= num_online_cpus || !online_mask[cpu])
                        continue;
                /* Set up performance monitoring on a CPU/Core */
                pefd = perf_event_open(&attr,0, -1, -1, 0);
                if (pefd < 0) {
                        fprintf(stderr, "Fail to set up performance monitor on a CPU/Core\n");
                        err = -1;
                        goto cleanup;
                }
                pefds[cpu] = pefd;

                //printf("perf event open");

                links[cpu] = bpf_program__attach_perf_event(skel->progs.func, pefd);
                if (!links[cpu]) {
                        err = -1;
                        goto cleanup;
                }
        }

 /* Wait and receive stack traces */
        int j=1;
        while(j) {j=j+1;}


cleanup:
        if (links) {
                for (cpu = 0; cpu < num_cpus; cpu++)
                        bpf_link__destroy(links[cpu]);
                free(links);
        }
        if (pefds) {
                for (i = 0; i < num_cpus; i++) {
                        if (pefds[i] >= 0)
                                close(pefds[i]);
                }
                free(pefds);
        }
        reproduce_bpf__destroy(skel);
        free(online_mask);
        return -err;
}

