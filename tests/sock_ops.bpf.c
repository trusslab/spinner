#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

#define LOCALHOST_IPV4 16777343

struct sock_key {
    __u32 sip;
    __u32 dip;
    __u32 sport;
    __u32 dport;
    __u32 family;
};

struct {
 __uint(type, BPF_MAP_TYPE_SOCKHASH);
 __uint(max_entries, 65535);
 __type(key, struct sock_key);
 __type(value, int);
} sock_ops_map SEC(".maps");

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("sockops")
int sock_ops_prog(struct bpf_sock_ops *skops) {
    // BPF program logic goes here
    bpf_printk("Sock_ops program\n");
    char * optval[10];
    long sockopt = bpf_getsockopt(skops, 1, 9, optval, 10);
    if (sockopt==0){
	    bpf_printk("Success\n");
    }
    else {
	    bpf_printk("Failure\n");
    }
    return 0;
}

