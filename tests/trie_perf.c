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
#include <signal.h>
#include <time.h>
#include "trie_perf.skel.h"
#include "trie_perf.h"


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
	//ret = syscall(__NR_perf_event_open, hw_event, 0,-1,-1,0);
        return ret;
}
 
void bump_memlock_rlimit(void)
{
        struct rlimit rlim_new = {
                .rlim_cur       = RLIM_INFINITY,
                .rlim_max       = RLIM_INFINITY,
        };

        if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
                fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
                exit(1);
        }
        return;
}
void handle_event(void *ctx, int cpu, void *data, unsigned int data_sz)
{
        
        const struct event *e = data;
        struct tm *tm;
        char ts[32];
        time_t t;

        time(&t);
        tm = localtime(&t);
        strftime(ts, sizeof(ts), "%H:%M:%S", tm);

        printf("%-8s %-5s %-7d %-16s %s\n", ts, "EXEC", e->pid, e->comm, e->filename);
        
        //printf("inside event handler");
        //exit(0);
        return;
}

static void lost_function(void *_ctx, int a, long long unsigned int d)
{
        printf("record lost\n");
        return;
}

int main(int argc, char *const argv[])
{       
        const char *online_cpus_file = "/sys/devices/system/cpu/online";
        int freq = 1, pid = -1, cpu;
        struct trie_perf_bpf *skel = NULL;
        struct perf_event_attr attr;
        struct bpf_link **links = NULL;
        struct trie_map *trie_m = NULL;
        int num_cpus, num_online_cpus;
        int *pefds = NULL, pefd;
        int argp, i, err = 0;
        bool *online_mask = NULL;

        struct bpf_program *prog;
        struct bpf_object *obj;
        struct bpf_map *map;
        char filename[256];
        
        struct perf_buffer *pb = NULL;
        struct perf_buffer_opts pb_opts = {};
        void *ctx;

        bump_memlock_rlimit();

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


        /*
        skel = map_perf_test2_bpf__open_and_load();
        if (!skel) {
                fprintf(stderr, "Fail to open and load BPF skeleton\n");
                err = -1;
                goto cleanup;
        }*/

        snprintf(filename, sizeof(filename), ".output/trie_perf.bpf.o");
        obj = bpf_object__open_file(filename, NULL);

        if (libbpf_get_error(obj)) {
                fprintf(stderr, "ERROR: opening BPF object file failed\n");
                //return 0;
                goto cleanup;
        }

        map = bpf_object__find_map_by_name(obj, "pb");
        if (libbpf_get_error(map)) {
                fprintf(stderr, "ERROR: finding a map in obj file failed\n");
                goto cleanup;
        }


        if (bpf_object__load(obj)) {
                fprintf(stderr, "ERROR: loading BPF object file failed\n");
                goto cleanup;
        }

        //change maps here
        /*
        array_m = array_map__new(bpf_map__fd(skel->maps.array_map), event_handler, NULL, NULL);
        if (!array_m) {
                err=-1;
                goto cleanup;
        }*/


        
        pefds = malloc(num_cpus * sizeof(int));
        for (i = 0; i < num_cpus; i++) {
                pefds[i] = -1;
        }

        links = calloc(num_cpus, sizeof(struct bpf_link *));


        memset(&attr, 0, sizeof(attr));

	/*	
	attr.freq =1;
	attr.inherit_stat = 1;
	attr.sample_period = 0;
	attr.inherit = 1;
	attr.size = sizeof(attr);
	attr.type = 8;
	attr.read_format = 0;
	attr.sample_type = 0;
	attr.config = 0 ;
	//attr.wakeup_events = 1;
	*/
	
	/*
	attr.type = PERF_TYPE_HARDWARE;
        attr.config = PERF_COUNT_HW_CPU_CYCLES;
        attr.sample_freq = 50;
        attr.inherit = 1;
        attr.freq = 1;
	*/
	
	
	attr.type = PERF_TYPE_SOFTWARE;
	attr.size = sizeof(attr);
	attr.config = PERF_COUNT_SW_CPU_CLOCK;
	attr.sample_freq = 10000;
	attr.freq = 1;
	attr.wakeup_events = 1;
	attr.sample_type = PERF_SAMPLE_TID | PERF_SAMPLE_CALLCHAIN | PERF_SAMPLE_STACK_USER;	
		

        for (cpu = 0; cpu < num_cpus; cpu++) {
                /* skip offline/not present CPUs */
                if (cpu >= num_online_cpus || !online_mask[cpu])
		{
			printf("in loop\n");
                        continue;
		}

                /* Set up performance monitoring on a CPU/Core */
                pefd = perf_event_open(&attr, pid, cpu, -1, 0);
		//pefd = perf_event_open(&attr, 0, -1, -1, 0);
                if (pefd < 0) {
                        fprintf(stderr, "Fail to set up performance monitor on a CPU/Core\n");
                        err = -1;
                        goto cleanup;
                }
                pefds[cpu] = pefd;
		printf("perf event opened\n");

                 /* Attach a BPF program on a CPU */

                /*
                links[cpu] = bpf_program__attach(prog);
                if (!links[cpu]) {
                        err = -1;
                        goto cleanup;
                }
                */

                /*
                bpf_object__for_each_program(prog, obj) {
                        links[cpu] = bpf_program__attach(prog);
                        if (libbpf_get_error(links[cpu])) {
                                fprintf(stderr, "ERROR: bpf_program__attach failed\n");
                                links[cpu] = NULL;
                                goto cleanup;
                        }
                }
                */

	        prog = bpf_object__find_program_by_name(obj, "trie_perf");
                //printf("%s", prog->name);
                if (!prog) {
                        fprintf(stderr, "ERROR: finding a prog in obj file failed\n");
                        goto cleanup;
                }

                
                //links[cpu] = bpf_program__attach(prog);
                links[cpu] = bpf_program__attach_perf_event(prog, pefds[cpu]);
                if (!links[cpu]) {
                        err = -1;
                        fprintf(stderr, "ERROR: bpf_program__attach failed\n");

                        goto cleanup;
                }
        
        }

        printf("Done!");

        /* Wait and receive stack traces */
        //while (array_map__poll(array_m, -1) >= 0) {}
        
        
        while (!exiting) {
                /*
                err = perf_buffer__poll(pb, 100);
                // Ctrl-C will cause -EINTR 
                if (err == -EINTR) {
                        err = 0;
                        break;
                }
                if (err < 0) {
                        printf("Error polling perf buffer: %d\n", err);
                        break;
                }
                */
        }

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
        //array_map__free(array_m);
        //perf_buffer__free(pb);
        trie_perf_bpf__destroy(skel);
        free(online_mask);
        return -err;
}

