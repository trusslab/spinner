#ifndef __TRIE_PERF_H
#define __TRIE_PERF_H

#define TASK_COMM_LEN 16
#define MAX_FILENAME_LEN 512


struct event {
        int pid;
        char comm[TASK_COMM_LEN];
        char filename[MAX_FILENAME_LEN];
};

struct ipv4_lpm_key {
        __u32 prefixlen;
        __u32 data;
};

#endif 


