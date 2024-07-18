#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
char LICENSE[] SEC("license") = "Dual BSD/GPL";
SEC("xdp.frags")
int test_prog(void *ctx){
struct bpf_map * param0;
const void * param1;
void * ret = bpf_map_lookup_elem( param0, param1);
return 0;
}
