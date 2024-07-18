#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <arpa/inet.h>

extern struct task_struct *bpf_task_acquire(struct task_struct *p) __ksym;

extern void bpf_task_release(struct task_struct *p) __ksym;


SEC("xdp_pass")
int xdp_pass_prog(struct xdp_md *ctx)
{
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    struct ethhdr *eth = data;
    __u16 h_proto;
    bpf_printk("bpf triggered by xpd_pass");

    struct task_struct *acquired;
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();

    acquired = bpf_task_acquire(task);
    if (acquired)
    {
            bpf_printk("task_acquired");
            bpf_task_release(acquired);
    }

    if (data + sizeof(struct ethhdr) > data_end)
        return XDP_DROP;

    h_proto = eth->h_proto;

    if (h_proto == htons(ETH_P_IPV6))
        return XDP_DROP;

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
