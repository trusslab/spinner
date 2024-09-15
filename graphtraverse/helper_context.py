import json

context_hierarchy = {'P': 0, 'S': 1, 'H':2, 'NMI':3}

actual_funcs = {
        "bpf_probe_read": ["bpf_probe_read_user", "bpf_probe_read_kernel"],
        "bpf_probe_read_str": ["bpf_probe_read_user_str", "bpf_probe_read_kernel_str"],
        "bpf_get_prandom_u32": ["bpf_user_rnd_u32"],
        "bpf_setsockopt": ["bpf_sk_setsockopt", "bpf_sock_addr_setsockopt", "bpf_sock_ops_setsockopt", 
            "bpf_unlocked_sk_setsockopt"],
        "bpf_getsockopt": ["bpf_sk_getsockopt", "bpf_unlocked_sk_getsockopt", "bpf_sock_addr_getsockopt",
            "bpf_sock_ops_getsockopt"],
        "bpf_fib_lookup": ["bpf_xdp_fib_lookup", "bpf_skb_fib_lookup"],
        "bpf_skb_output": ["bpf_skb_event_output"],
        "bpf_xdp_output": ["bpf_xdp_output"],
        "bpf_get_func_arg": ["get_func_arg"],
        "bpf_get_func_arg_cnt": ["get_func_arg_cnt"],
        "bpf_get_func_ret": ["get_func_ret"],
        "bpf_lwt_push_encap": ["bpf_lwt_in_push_encap", "bpf_lwt_xmit_push_encap"],
        "bpf_get_netns_cookie": ["bpf_get_netns_cookie_sock", "bpf_get_netns_cookie_sock_addr",
            "bpf_get_netns_cookie_sock_ops", "bpf_get_netns_cookie_sk_msg", "bpf_get_netns_cookie_sockopt"],
        "bpf_load_hdr_opt": ["bpf_sock_ops_load_hdr_opt"],
        "bpf_store_hdr_opt": ["bpf_sock_ops_store_hdr_opt"],
        "bpf_reserve_hdr_opt": ["bpf_sock_ops_reserve_hdr_opt"],
        "bpf_get_func_ip": ["bpf_get_func_ip_tracing", "bpf_get_func_ip_kprobe_multi", 
            "bpf_get_func_ip_uprobe_multi", "bpf_get_func_ip_kprobe"]
        }

def transform_context(type_context):
    irqs_hierarchy = {'.': 0, 'b':1, 'd':2}
   
    for progtype in type_context:
        if irqs_hierarchy[type_context[progtype][1]]>context_hierarchy[type_context[progtype][0]]:
            if type_context[progtype][1] == 'b':
                type_context[progtype] = 'S'
            else:
                type_context[progtype] = 'H'
        else:
            type_context[progtype] = type_context[progtype][0]
    return type_context


def helper_context():
    with open('../fptests/output/helper-progtype.json', 'r') as file:
       helper_progtype = json.load(file)
    with open('../utils/output/prog_type-context.json', 'r') as file:
        progtype_context = json.load(file)
    progtype_context = transform_context(progtype_context)

    helper_context = {}
    for helper in helper_progtype:
        context = ''
        for progtype in progtype_context:
            if progtype in helper_progtype[helper][0]:
                if context=='':
                    context = progtype_context[progtype]
                if context_hierarchy[progtype_context[progtype]]>context_hierarchy[context]:
                    context = progtype_context[progtype]
        if helper not in actual_funcs:
            helper_context[helper] = context
        else:
            for actual_func in actual_funcs:
                helper_context[actual_func] = context
        
    for progtype in helper_progtype['bpf_map_update_elem'][0]:
        if progtype not in progtype_context:
            print(progtype+" not in dynamic analysis")
   

    print(helper_context)
    return helper_context



if __name__ == "__main__":
    helper_context()
