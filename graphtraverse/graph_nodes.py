import json
from helper_context import helper_context

function_list_helpers_1 = {
        "bpf_xdp_get_buff_len" : "NMI",
        "__bpf_setsockopt" : "S",
        "bpf_tcp_sock" : "S",
        "bpf_skb_load_bytes" : "S",
        "bpf_flow_dissector_load_bytes" : "P",
        "sk_reuseport_load_bytes": "S",
        "bpf_skb_load_bytes_relative" : "S",
        "sk_reuseport_load_bytes_relative" : "S",
        "bpf_get_socket_cookie" : "NMI",
        "bpf_get_socket_uid" : "S",
        "bpf_skc_to_tcp6_sock" : "NMI",
        "bpf_skc_to_tcp_sock" : "NMI",
        "bpf_skc_to_tcp_timewait_sock" : "NMI",
        "bpf_skc_to_tcp_request_sock": "NMI",
        "bpf_skc_to_udp6_sock" : "NMI",
        "bpf_skc_to_unix_sock" : "NMI",
        "bpf_skc_to_mptcp_sock" : "NMI",
        "bpf_skb_store_bytes" : "S",
        "bpf_skb_pull_data" : "S",
        "bpf_csum_diff" : "S",
        "bpf_csum_update" : "S",
        "bpf_csum_level" : "S",
        "bpf_l3_csum_replace" : "S",
        "bpf_l4_csum_replace" : "S",
        "bpf_clone_redirect" : "S",
        "bpf_redirect" : "S",
        "bpf_xdp_redirect" : "S",
        #"bpf_redirect_map" : "None",
        "bpf_xdp_redirect_map" : "S",
        "bpf_get_cgroup_classid" : "S",
        "bpf_get_cgroup_classid_curr" : "S",
        "bpf_skb_vlan_push" : "S",
        "bpf_skb_vlan_pop" : "S",
        "bpf_skb_change_proto" : "S",
        "bpf_skb_change_type" : "S",
        "bpf_skb_adjust_room" : "S",
        "bpf_skb_change_tail" : "S",
        "bpf_skb_change_head" : "S",
        "bpf_skb_get_tunnel_key" : "S",
        "bpf_skb_get_tunnel_opt" : "S",
        "bpf_redirect_neigh" : "S",
        "bpf_redirect_peer" : "S",
        "bpf_get_route_realm" : "S",
        "bpf_get_hash_recalc" : "S",
        "bpf_set_hash_invalid" : "S",
        "bpf_set_hash" : "S",
        "bpf_skb_under_cgroup": "S",
        "bpf_sk_fullsock" : "S",
        "bpf_skb_get_xfrm_state" : "S",
        "bpf_skb_cgroup_classid" : "S",
        "bpf_skb_cgroup_id" : "S",
        "bpf_skb_ancestor_cgroup_id" : "S",
        "bpf_sk_release" : "S",
        "bpf_get_listener_sock" : "S",
        "bpf_tcp_check_syncookie" : "S",
        "bpf_skb_ecn_set_ce" : "S",
        "bpf_tcp_gen_syncookie" : "S",
        "bpf_sk_assign" : "S",
        "bpf_sk_lookup_assign" : "S",
        "bpf_skb_set_tstamp" : "S",
        "bpf_tcp_raw_gen_syncookie_ipv4" : "S",
        "bpf_tcp_raw_gen_syncookie_ipv6" : "S",
        "bpf_tcp_raw_check_syncookie_ipv4" : "S",
        "bpf_tcp_raw_check_syncookie_ipv6" : "S",
        "bpf_skb_set_tunnel_key": "S",
        "bpf_skb_set_tunnel_opt" : "S",
        "bpf_xdp_adjust_head" : "S",
        "bpf_xdp_adjust_meta" : "S",
        "bpf_xdp_adjust_tail" : "S",
        "bpf_xdp_load_bytes" : "S",
        "bpf_xdp_store_bytes" : "S",
        "bpf_sk_cgroup_id" : "S",
        "bpf_sk_ancestor_cgroup_id" : "S",
        "bpf_sk_lookup_tcp" : "S",
        "bpf_sock_addr_sk_lookup_tcp" : "P",
        "bpf_xdp_sk_lookup_tcp" : "S",
        "bpf_tc_sk_lookup_tcp" : "S",
        "bpf_sk_lookup_udp" : "S",
        "bpf_sock_addr_sk_lookup_tcp" : "P",
        "bpf_xdp_sk_lookup_tcp" : "S",
        "bpf_tc_sk_lookup_tcp" : "S",
        "bpf_skc_lookup_tcp" : "S",
        "bpf_sock_addr_skc_lookup_tcp" : "P",
        "bpf_xdp_skc_lookup_tcp" : "S",
        "bpf_tc_skc_lookup_tcp" : "S",
        "bpf_bind" : "P",
        "bpf_sock_ops_cb_flags_set" : "S",
        "bpf_msg_apply_bytes": "P",
        "bpf_msg_cork_bytes" : "P",
        "bpf_msg_pull_data" : "P",
        "bpf_msg_push_data" : "P",
        "bpf_msg_pop_data" : "P",
        "bpf_sock_from_file" : "NMI",
        "bpf_lwt_in_push_encap" : "P",
        "bpf_lwt_xmit_push_encap" : "P",

        "bpf_map_lookup_elem" : "NMI",
        "bpf_map_update_elem" : "NMI",
        "bpf_map_delete_elem" : "NMI",
        #"bpf_probe_read / bpf_probe_read_str" : "missing",
        "bpf_probe_read_user" : "NMI",
        "bpf_probe_read_user_str" : "NMI",
        "bpf_probe_read_kernel" : "NMI",
        "bpf_probe_read_kernel_str" : "NMI",
        "bpf_ktime_get_ns" : "NMI",
        "bpf_trace_printk" : "NMI",
        "bpf_user_rnd_u32" : "NMI", #"bpf_get_prandom_u32" : "H",
        "bpf_get_smp_processor_id" : "S",
        #"bpf_tail_call" : "NMI",  #no implementation
        "bpf_get_current_pid_tgid" : "P",
        "bpf_get_current_uid_gid" : "P",
        "bpf_get_current_comm" : "P",
        "bpf_get_cgroup_classid" : "S",
        "bpf_perf_event_read" : "unknown",
        "bpf_perf_event_output" : "NMI",
        "bpf_event_output_data" : "S",  
        "bpf_skb_event_output" : "S",
        "bpf_xdp_event_output" : "S",
        "bpf_get_stackid" : "NMI",
        "bpf_get_current_task" : "NMI",
        "bpf_probe_write_user" : "unknown",
        "bpf_current_task_under_cgroup" : "unknown",
        "bpf_get_numa_node_id" : "NMI",
        "bpf_sk_redirect_map" : "S",
        "bpf_sock_map_update" : "S",
        "bpf_perf_event_read_value" : "unknown",
        "bpf_perf_prog_read_value" : "NMI",
        "__bpf_getsockopt" : "None",
        "bpf_sock_ops_getsockopt" : "S",
        "bpf_sk_getsockopt" : "P",
        "bpf_unlocked_sk_getsockopt" : "P",
        "bpf_sock_addr_getsockopt" : "P",
        "bpf_override_return" : "P",
        "bpf_msg_redirect_map" : "P",
        "bpf_get_stack" : "NMI",
        #"bpf_fib_lookup" : "None",
        "bpf_xdp_fib_lookup" : "S",
        "bpf_skb_fib_lookup" : "S",
        "bpf_sock_hash_update" : "S",
        "bpf_msg_redirect_hash" : "P",
        "bpf_sk_redirect_hash" : "S",
        "bpf_lwt_seg6_store_bytes" : "P",
        "bpf_lwt_seg6_adjust_srh" : "P",
        "bpf_lwt_seg6_action" : "P",
        "bpf_rc_repeat" : "P",
        "bpf_rc_keydown" : "P",
        "bpf_get_current_cgroup_id" : "NMI",
        "bpf_get_local_storage" : "S",
        "sk_select_reuseport" : "S", #bpf_sk_select_reuseport
        "bpf_map_push_elem" : "NMI",
        "bpf_map_pop_elem" : "NMI",
        "bpf_map_peek_elem" : "NMI",
        "bpf_rc_pointer_rel" : "P",
        "bpf_spin_lock" : "NMI",
        "bpf_spin_unlock" : "NMI",
        "bpf_sysctl_get_name" : "P",
        "bpf_sysctl_get_current_value" : "P",
        "bpf_sysctl_get_new_value" : "P",
        "bpf_sysctl_set_new_value" : "P",
        "bpf_strtol" : "NMI",
        "bpf_strtoul" : "NMI",
        "bpf_sk_storage_get" : "S",
        #"bpf_sk_storage_get_cg_sock" : "P", #implementation same as bpf_sk_storage_get
        "bpf_sk_storage_get_tracing" : "NMI",
        "bpf_sk_storage_delete" : "S",
        "bpf_sk_storage_delete_tracing" : "NMI",
        "bpf_send_signal" : "unknown",
        #"bpf_skb_output" : "NMI",  #implementation same as skb_event_output
        "bpf_tcp_send_ack" : "P",
        "bpf_send_signal_thread" : "unknown",
        "bpf_jiffies64" : "NMI",
        "bpf_read_branch_records" : "NMI",
        "bpf_get_ns_current_pid_tgid" : "unknown",
        #"bpf_xdp_output" : "NMI",  #implementation same as xdp_event_output
        #"bpf_get_netns_cookie" : "None",
        "bpf_get_netns_cookie_sock_addr" : "P",
        "bpf_get_netns_cookie_sock" : "P",
        "bpf_get_netns_cookie_sock_ops" : "S",
        "bpf_get_netns_cookie_sk_msg" : "P",
        "bpf_get_netns_cookie_sockopt" : "P",
        "bpf_get_current_ancestor_cgroup_id" : "NMI",
        "bpf_ktime_get_boot_ns" : "NMI",
        "bpf_seq_printf" : "NMI",
        "bpf_seq_write" : "NMI",
        "bpf_ringbuf_output" : "NMI",
        "bpf_ringbuf_reserve" : "NMI",
        "bpf_ringbuf_submit" : "NMI",
        "bpf_ringbuf_discard" : "NMI",
        "bpf_ringbuf_query" : "NMI",
        "bpf_get_task_stack" : "unknown",
        #"bpf_load_hdr_opt" : "none", #implementation same as bpf_sock_ops_load_hdr_opt
        "bpf_sock_ops_load_hdr_opt" : "S",
        #"bpf_store_hdr_opt" : "none", #implementation same as bpf_sock_ops_store_hdr_opt
        "bpf_sock_ops_store_hdr_opt" : "S",
        #"bpf_reserve_hdr_opt" : "none", #implementation same as bpf_sock_ops_reserve_hdr_opt
        "bpf_sock_ops_reserve_hdr_opt" : "S",
        "bpf_inode_storage_get": "P",
        "bpf_inode_storage_delete" : "P",
        "bpf_d_path" : "NMI",
        "bpf_copy_from_user" : "unknown",
        "bpf_snprintf_btf" : "NMI",
        "bpf_seq_printf_btf" : "NMI",
        "bpf_per_cpu_ptr" : "NMI",
        "bpf_this_cpu_ptr" : "NMI",
        "bpf_task_storage_get" : "unknown",
        "bpf_task_storage_delete" : "unknown",
        "bpf_get_current_task_btf" : "NMI",
        "bpf_bprm_opts_set" : "P",
        "bpf_ktime_get_coarse_ns" : "S",
        "bpf_ima_inode_hash" : "P",
        #"bpf_check_mtu" : "none",
        "bpf_xdp_check_mtu" : "S", 
        "bpf_skb_check_mtu" : "S",
        "bpf_for_each_map_elem" : "NMI",
        "bpf_snprintf" : "NMI",
        "bpf_sys_bpf" : "P",
        "bpf_btf_find_by_name_kind" : "P",
        "bpf_sys_close" : "P",
        "bpf_timer_init" : "NMI",
        "bpf_timer_set_callback" : "NMI",
        "bpf_timer_start" : "NMI",
        "bpf_timer_cancel" : "NMI",
        #"bpf_get_func_ip" : "none",
        "bpf_get_func_ip_kprobe" : "P",
        "bpf_get_func_ip_kprobe_multi" : "P",
        "bpf_get_func_ip_uprobe_multi" : "P",
        "bpf_get_attach_cookie" : "P",
        "bpf_get_attach_cookie_tracing" : "NMI",
        "bpf_get_attach_cookie_kprobe_multi" : "P", #implementation for bpf_get_attach_cookie_kmulti
        "bpf_get_attach_cookie_uprobe_multi" : "P", #implementation for bpf_get_attach_cookie_umulti
        "bpf_get_attach_cookie_trace" : "H",
        "bpf_get_attach_cookie_pe" : "NMI",
        "bpf_task_pt_regs" : "NMI",
        "bpf_get_branch_snapshot" : "unknown",
        "bpf_trace_vprintk" : "NMI",
        "bpf_kallsyms_lookup_name" : "P",
        "bpf_find_vma" : "unknown",
        "bpf_loop" : "NMI",
        "bpf_strncmp" : "NMI",
        "get_func_arg" : "NMI", #implementation for bpf_get_func_arg
        "get_func_ret" : "NMI", #implementation for bpf_get_func_ret
        "get_func_arg_cnt" : "NMI", #implementation for bpf_get_func_arg_cnt
        "bpf_get_retval" : "S",
        "bpf_set_retval" : "S",
        "bpf_copy_from_user_task" : "unknown",
        "bpf_ima_file_hash": "P",
        "bpf_kptr_xchg" : "NMI",
        "bpf_map_lookup_percpu_elem" : "NMI",
        "bpf_dynptr_from_mem" : "NMI",
        "bpf_ringbuf_reserve_dynptr" : "NMI",
        "bpf_ringbuf_submit_dynptr" : "NMI",
        "bpf_ringbuf_discard_dynptr" : "NMI",
        "bpf_dynptr_read" : "NMI",
        "bpf_dynptr_write" : "NMI",
        "bpf_dynptr_data" : "NMI",
        "bpf_ktime_get_tai_ns" : "NMI",
        "bpf_user_ringbuf_drain" : "NMI",
        "bpf_cgrp_storage_get" : "NMI",
        "bpf_cgrp_storage_delete" : "NMI"
}

function_list_array = {
        "array_map_lookup_elem" : "NMI",
        "array_map_update_elem" : "NMI",
        "array_map_delete_elem" : "NMI",
        "bpf_for_each_array_elem" : "NMI",
        }
        

function_list_percpu_array = {
        "percpu_array_map_lookup_elem" : "NMI",
        "array_map_update_elem" : "NMI",
        "array_map_delete_elem" : "NMI",
        "percpu_array_map_lookup_percpu_elem" : "NMI",
        "bpf_for_each_array_elem" : "NMI",
        }

function_list_perf_event_array = {
        }

function_list_cgroup_array = {
        }

function_list_prog_array = {
        }

function_list_array_of_maps = {
        "array_of_map_lookup_elem" : "NMI",
        }

function_list_bloom_filter = {
        "bloom_map_push_elem" : "NMI",
        "bloom_map_peek_elem" : "NMI",
        }

function_list_htab = {
        "htab_map_lookup_elem" : "NMI",
        "htab_map_update_elem" : "NMI",
        "htab_map_delete_elem" : "NMI",
        "bpf_for_each_hash_elem" : "NMI",
        }

function_list_htab_lru = {
        "htab_lru_map_lookup_elem" : "NMI",
        "htab_lru_map_update_elem" : "NMI",
        "htab_lru_map_delete_elem" : "NMI",
        "bpf_for_each_hash_elem" : "NMI",
        }

function_list_htab_percpu = {
        "htab_percpu_map_lookup_elem" : "NMI",
        "htab_percpu_map_update_elem" : "NMI",
        "htab_map_delete_elem" : "NMI",
        "htab_percpu_map_lookup_percpu_elem" : "NMI",
        "bpf_for_each_hash_elem" : "NMI",
        }

function_list_htab_lru_percpu = {
        "htab_lru_percpu_map_lookup_elem" : "NMI",
        "htab_lru_percpu_map_update_elem" : "NMI",
        "htab_lru_map_delete_elem" : "NMI",
        "htab_lru_percpu_map_lookup_percpu_elem" : "NMI",
        "bpf_for_each_hash_elem" : "NMI",
        }

function_list_htab_of_maps = {
        "htab_of_map_lookup_elem" : "NMI",
        }

function_list_stack_trace = { 
        }

function_list_trie = {
        "trie_lookup_elem" : "NMI",
        "trie_update_elem" : "NMI",
        "trie_delete_elem" : "NMI",
        }

function_list_dev = {
        "dev_map_lookup_elem" : "S",
        "dev_map_redirect" : "S"
        }

function_list_dev_hash = {
        "dev_map_hash_lookup_elem" : "S",
        "dev_hash_map_redirect" : "S",
        }

function_list_sock = {
        "sock_map_update_elem" : "S",
        "sock_map_delete_elem" : "S",
        "sock_map_lookup" : "S",
        }

function_list_sock_hash = {
        "sock_hash_delete_elem" : "S",
        "sock_map_update_elem" : "S",
        "sock_hash_lookup" : "S",
        }

function_list_cpu = {
        "cpu_map_redirect" : "S"
        }

function_list_xsk = {
        "xsk_map_lookup_elem" : "S",
        }

function_list_reuseport_array = {
        }

function_list_stack = {
        "queue_stack_map_push_elem" : "NMI",
        "stack_map_pop_elem" : "NMI",
        "stack_map_peek_elem" : "NMI",
        }

function_list_queue = {
        "queue_stack_map_push_elem" : "NMI",
        "queue_map_pop_elem" : "NMI",
        "queue_map_peek_elem" : "NMI",
}

function_list_sk_storage = {
        }

function_list_struct_ops = {
        }

function_list_ringbuf = {
        "ringbuf_map_lookup_elem" : "NMI",
        "ringbuf_map_update_elem" : "NMI",
        "ringbuf_map_delete_elem" : "NMI",
        }

function_list_inode_storage = {
        }

function_list_task_storage = {
        }

function_list_user_ringbuf = {
        }


function_list_cgrp_storage = {
        }

function_list_arena = {
        "arena_map_push_elem" : "NMI",
        "arena_map_peek_elem" : "NMI",
        "arena_map_pop_elem" : "NMI",
        }

kfunc_list = {
        "hid_bpf_get_data" : "H",
        "hid_bpf_attach_prog" : "P",
        "hid_bpf_allocate_context" : "P",
        "hid_bpf_release_context" : "P",
        "hid_bpf_hw_request" : "P",
        "bpf_get_fsverity_digest" : "P",
        "bpf_arena_alloc_pages" : "NMI",
        "bpf_arena_free_pages" : "NMI",
        "bpf_iter_num_new" : "NMI",
        "bpf_iter_num_next" : "NMI",
        "bpf_iter_num_destroy" : "NMI",
        "bpf_iter_css_new" : "NMI",
        "bpf_iter_css_next" : "NMI",
        "bpf_iter_css_destroy" : "NMI",
        "bpf_cpumask_create" : "H",
        "bpf_cpumask_acquire" : "H",
        "bpf_cpumask_release" : "H",
        "bpf_cpumask_release_dtor" : "P",
        "bpf_cpumask_first" : "H",
        "bpf_cpumask_first_zero" : "H",
        "bpf_cpumask_set_cpu" : "H",
        "bpf_cpumask_clear_cpu" : "H",
        "bpf_cpumask_test_cpu" : "H",
        "bpf_cpumask_test_and_set_cpu" : "H",
        "bpf_cpumask_test_and_clear_cpu" :"H",
        "bpf_cpumask_setall" : "H",
        "bpf_cpumask_clear" : "H",
        "bpf_cpumask_and" : "H",
        "bpf_cpumask_or" : "H",
        "bpf_cpumask_xor" : "H",
        "bpf_cpumask_equal" : "H",
        "bpf_cpumask_intersects" : "H",
        "bpf_cpumask_subset" : "H",
        "bpf_cpumask_empty" : "H",
        "bpf_cpumask_full" : "H",
        "bpf_cpumask_copy" : "H",
        "bpf_cpumask_any_distribute" : "H",
        "bpf_cpumask_any_and_distribute" : "H",
        "bpf_cpumask_weight" : "H",
        "bpf_obj_new_impl" : "H",
        "bpf_percpu_obj_new_impl" : "H",
        "bpf_obj_drop_impl" : "H",
        "bpf_percpu_obj_drop_impl" : "H",
        "bpf_refcount_acquire_impl" : "H",
        "bpf_list_push_front_impl" : "H",
        "bpf_list_push_back_impl" : "H",
        "bpf_list_pop_front" : "H",
        "bpf_list_pop_back" : "H",
        "bpf_rbtree_remove" : "H",
        "bpf_rbtree_add_impl" : "H",
        "bpf_rbtree_first" : "H",
        "bpf_task_acquire" : "H",
        "bpf_task_release" : "H",
        "bpf_task_release_dtor" : "P",
        "bpf_cgroup_acquire" : "H",
        "bpf_cgroup_release" : "H",
        "bpf_cgroup_release_dtor" : "P",
        "bpf_cgroup_ancestor" : "H",
        "bpf_cgroup_from_id" : "H",
        "bpf_task_under_cgroup" : "H",
        "bpf_task_get_cgroup1" : "H",
        "bpf_task_from_pid" : "H",
        "bpf_dynptr_slice" : "NMI",
        "bpf_dynptr_slice_rdwr" : "NMI",
        "bpf_dynptr_adjust" : "NMI",
        "bpf_dynptr_is_null" : "NMI",
        "bpf_dynptr_is_rdonly" : "NMI",
        "bpf_dynptr_size" : "NMI",
        "bpf_dynptr_clone" : "NMI",
        "bpf_cast_to_kern_ctx" : "NMI",
        "bpf_rdonly_cast" : "NMI",
        "bpf_rcu_read_lock" : "NMI",
        "bpf_rcu_read_unlock" : "NMI",
        "bpf_throw" : "H",
        "bpf_map_sum_elem_count" : "NMI",
        "bpf_iter_task_vma_new" : "NMI",
        "bpf_iter_task_vma_next" : "NMI",
        "bpf_iter_task_vma_destroy" : "NMI",
        "bpf_iter_css_task_new" : "NMI",
        "bpf_iter_css_task_next" : "NMI",
        "bpf_iter_css_task_destroy" : "NMI",
        "bpf_iter_task_new" : "NMI",
        "bpf_iter_task_next" : "NMI",
        "bpf_iter_task_destroy" : "NMI",
        "cgroup_rstat_updated" : "H",
        "cgroup_rstat_flush" : "H",
        "crash_kexec" : "H",
        "bpf_fentry_test1" : "",
        "bpf_fentry_test9" : "",
        "bpf_modify_return_test" : "",
        "bpf_modify_return_test2" : "",
        "bpf_kfunc_call_test_release" : "H",
        "bpf_kfunc_call_test_release_dtor" : "P",
        "bpf_kfunc_call_memb_release" : "H",
        "bpf_kfunc_call_memb_release_dtor" : "P",
        "bpf_dynptr_from_skb" : "S",
        "bpf_dynptr_from_xdp" : "S",
        "bpf_sock_addr_set_sun_path" : "P",
        "bpf_sk_assign_tcp_reqsk" : "S",
        "bpf_sock_destroy" : "",
        "bpf_xdp_metadata_rx_timestamp" : "S",
        "bpf_xdp_metadata_rx_hash" : "S",
        "bpf_xdp_metadata_rx_vlan_tag" : "S",
        "bpf_skb_set_fou_encap" : "S",
        "bpf_skb_get_fou_encap" : "S",
        "bbr_min_tso_segs" : "P",
        "bbr_cwnd_event" : "P",
        "bbr_main" : "P",
        "bbr_init" : "P",
        "bbr_sndbuf_expand": "P",
        "bbr_undo_cwnd": "P",
        "bbr_ssthresh" : "P",
        "bbr_set_state" : "P",
        "tcp_slow_start" : "P",
        "tcp_cong_avoid_ai" : "P",
        "tcp_reno_cong_avoid" : "P",
        "tcp_reno_ssthresh" : "P",
        "tcp_reno_undo_cwnd" : "P", 
        "cubictcp_init" : "P",
        "cubictcp_cwnd_event" : "P",
        "cubictcp_cong_avoid" : "P",
        "cubictcp_recalc_ssthresh" : "P",
        "cubictcp_state": "P",
        "cubictcp_acked" : "P",
        "dctcp_init" : "P",
        "dctcp_ssthresh" : "P",
        "dctcp_update_alpha" : "P",
        "dctcp_state" : "P",
        "dctcp_cwnd_event" : "P",
        "dctcp_cwnd_undo" : "P",
        "bpf_xdp_ct_alloc" : "S",
        "bpf_xdp_ct_lookup" : "S",
        "bpf_skb_ct_alloc" : "S",
        "bpf_skb_ct_lookup" : "S",
        "bpf_ct_insert_entry" : "S",
        "bpf_ct_release" : "S",
        "bpf_ct_set_timeout" : "S",
        "bpf_ct_change_timeout" : "S",
        "bpf_ct_set_status" : "S",
        "bpf_ct_change_status" : "S",
        "bpf_ct_set_nat_info" : "S",
        "bpf_skb_get_xfrm_info" : "S",
        "bpf_skb_set_xfrm_info" : "S",
        "bpf_xdp_get_xfrm_state" : "S",
        "bpf_xdp_xfrm_state_release" : "S",
        }

function_lists = [function_list_array, function_list_percpu_array, function_list_prog_array, function_list_perf_event_array, 
        function_list_cgroup_array, function_list_array_of_maps, function_list_bloom_filter, function_list_htab, function_list_htab_lru, 
        function_list_htab_percpu, function_list_htab_lru_percpu , function_list_htab_of_maps, function_list_stack_trace, function_list_trie,
        function_list_dev, function_list_dev_hash, function_list_sock, function_list_sock_hash, function_list_cpu, function_list_xsk,
        function_list_reuseport_array, function_list_stack, function_list_queue, function_list_sk_storage, function_list_struct_ops, function_list_ringbuf,
        function_list_inode_storage, function_list_task_storage, function_list_user_ringbuf, function_list_cgrp_storage, function_list_arena, kfunc_list] 
node_list = {}


def get_nodes(graph_file_name):
    graph_file = open(graph_file_name, 'r')

    function_list_helpers = helper_context();
    function_lists.append(function_list_helpers)

    for function in function_list_helpers:
        if function not in function_list_helpers_1:
            print(function+" not tested");
    

    for list in function_lists:
        for key in list:
            flag = False
            while True:
                line = graph_file.readline()
                #print(line)
                if not line:
                    break
                #if key in line and key==line[line.index("fun:")+5 : line.rindex("\\")]: ##for SVF gen callgraphs
                if key in line and key==line[line.index("fun:")+5 : line.rindex("}")]:  ##for mlta gen callgraphs
                    flag = True
                    #node_list[line[1:19]]=list[key] ##for SVF gen callgraphs
                    node_list[line[:line.index("[")-1]]=list[key] ##for mlta gen callgraphs
            if flag==False:
                print("Node matching "+key+" not found.")
            graph_file.seek(0)
            


    json_object = json.dumps(node_list)

    with open('nodes.json', "w") as outfile:
        outfile.write(json_object)

