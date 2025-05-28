import json
from helper_context import helper_context

function_list_array = {
        "array_map_lookup_elem" : ["NMI", "not-sleepable", 1],
        "array_map_update_elem" : ["NMI", "not-sleepable", 1],
        "array_map_delete_elem" : ["NMI", "not-sleepable", 1],
        "bpf_for_each_array_elem" : ["NMI", "not-sleepable", 1],
        }
        

function_list_percpu_array = {
        "percpu_array_map_lookup_elem" : ["NMI", "not-sleepable", 1],
        "array_map_update_elem" : ["NMI", "not-sleepable", 1],
        "array_map_delete_elem" : ["NMI", "not-sleepable", 1],
        "percpu_array_map_lookup_percpu_elem" : ["NMI", "not-sleepable", 1],
        "bpf_for_each_array_elem" : ["NMI", "not-sleepable", 1],
        }

function_list_perf_event_array = {
        }

function_list_cgroup_array = {
        }

function_list_prog_array = {
        }

function_list_array_of_maps = {
        "array_of_map_lookup_elem" : ["NMI", "not-sleepable", 1],
        }

function_list_bloom_filter = {
        "bloom_map_push_elem" : ["NMI", "not-sleepable", 1],
        "bloom_map_peek_elem" : ["NMI", "not-sleepable", 1]
        }

function_list_htab = {
        "htab_map_lookup_elem" : ["NMI", "not-sleepable", 1],
        "htab_map_update_elem" : ["NMI", "not-sleepable", 1],
        "htab_map_delete_elem" : ["NMI", "not-sleepable", 1],
        "bpf_for_each_hash_elem" : ["NMI", "not-sleepable", 1]
        }

function_list_htab_lru = {
        "htab_lru_map_lookup_elem" : ["NMI", "not-sleepable", 1],
        "htab_lru_map_update_elem" : ["NMI","not-sleepable", 1],
        "htab_lru_map_delete_elem" : ["NMI","not-sleepable", 1],
        "bpf_for_each_hash_elem" : ["NMI","not-sleepable", 1],
        }

function_list_htab_percpu = {
        "htab_percpu_map_lookup_elem" : ["NMI","not-sleepable", 1],
        "htab_percpu_map_update_elem" : ["NMI","not-sleepable", 1],
        "htab_map_delete_elem" : ["NMI","not-sleepable", 1],
        "htab_percpu_map_lookup_percpu_elem" : ["NMI","not-sleepable", 1],
        "bpf_for_each_hash_elem" : ["NMI","not-sleepable", 1],
        }

function_list_htab_lru_percpu = {
        "htab_lru_percpu_map_lookup_elem" : ["NMI","not-sleepable", 1],
        "htab_lru_percpu_map_update_elem" : ["NMI","not-sleepable", 1],
        "htab_lru_map_delete_elem" : ["NMI","not-sleepable", 1],
        "htab_lru_percpu_map_lookup_percpu_elem" : ["NMI","not-sleepable", 1],
        "bpf_for_each_hash_elem" : ["NMI","not-sleepable", 1],
        }

function_list_htab_of_maps = {
        "htab_of_map_lookup_elem" : ["NMI","not-sleepable", 1],
        }

function_list_stack_trace = { 
        }

function_list_trie = {
        "trie_lookup_elem" : ["NMI","not-sleepable", 1],
        "trie_update_elem" : ["NMI","not-sleepable", 1],
        "trie_delete_elem" : ["NMI","not-sleepable", 1],
        }

function_list_dev = {
        "dev_map_lookup_elem" : ["S","not-sleepable", 1],
        "dev_map_redirect" : ["S","not-sleepable"],
        }

function_list_dev_hash = {
        "dev_map_hash_lookup_elem" : ["S","not-sleepable", 1],
        "dev_hash_map_redirect" : ["S","not-sleepable"],
        }

function_list_sock = {
        "sock_map_update_elem" : ["S","not-sleepable"],
        "sock_map_delete_elem" : ["S","not-sleepable"],
        "sock_map_lookup" : ["S","not-sleepable"],
        }

function_list_sock_hash = {
        "sock_hash_delete_elem" : ["S","not-sleepable"],
        "sock_map_update_elem" : ["S","not-sleepable"],
        "sock_hash_lookup" : ["S","not-sleepable"],
        }

function_list_cpu = {
        "cpu_map_redirect" : ["S","not-sleepable"],
        }

function_list_xsk = {
        "xsk_map_lookup_elem" : ["S","not-sleepable", 1],
        "xsk_map_redirect" : ["S","not-sleepable"]
        }

function_list_reuseport_array = {
        }

function_list_stack = {
        "queue_stack_map_push_elem" : ["NMI","not-sleepable", 1],
        "stack_map_pop_elem" : ["NMI","not-sleepable", 1],
        "stack_map_peek_elem" : ["NMI","not-sleepable", 1],
        }

function_list_queue = {
        "queue_stack_map_push_elem" : ["NMI","not-sleepable", 1],
        "queue_map_pop_elem" : ["NMI","not-sleepable", 1],
        "queue_map_peek_elem" : ["NMI","not-sleepable",1],
}

function_list_sk_storage = {
        }

function_list_struct_ops = {
        }

function_list_ringbuf = {
        "ringbuf_map_lookup_elem" : ["NMI","not-sleepable", 1],
        "ringbuf_map_update_elem" : ["NMI","not-sleepable", 1],
        "ringbuf_map_delete_elem" : ["NMI","not-sleepable", 1],
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
        "arena_map_push_elem" : ["NMI","not-sleepable",1],
        "arena_map_peek_elem" : ["NMI","not-sleepable, 1"],
        "arena_map_pop_elem" : ["NMI","not-sleepable", 1],
        }

kfunc_list = {
        "hid_bpf_get_data" : ["NMI","not-sleepable", 1],
        "hid_bpf_attach_prog" : ["P","not-sleepable"],
        "hid_bpf_allocate_context" : ["P","not-sleepable"],
        "hid_bpf_release_context" : ["P","not-sleepable"],
        "hid_bpf_hw_request" : ["P","not-sleepable"],
        "bpf_get_fsverity_digest" : ["P","not-sleepable"],
        "bpf_arena_alloc_pages" : ["NMI","sleepable", 1],
        "bpf_arena_free_pages" : ["NMI","sleepable", 1],
        "bpf_iter_num_new" : ["NMI","not-sleepable", 1],
        "bpf_iter_num_next" : ["NMI","not-sleepable",1],
        "bpf_iter_num_destroy" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_new" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_next" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_destroy" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_create" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_acquire" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_release" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_release_dtor" : ["P","not-sleepable", 1],
        "bpf_cpumask_first" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_first_zero" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_set_cpu" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_clear_cpu" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_test_cpu" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_test_and_set_cpu" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_test_and_clear_cpu" :["NMI","not-sleepable", 1],
        "bpf_cpumask_setall" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_clear" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_and" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_or" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_xor" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_equal" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_intersects" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_subset" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_empty" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_full" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_copy" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_any_distribute" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_any_and_distribute" : ["NMI","not-sleepable", 1],
        "bpf_cpumask_weight" : ["NMI","not-sleepable", 1],
        "bpf_obj_new_impl" : ["NMI","not-sleepable", 1],
        "bpf_percpu_obj_new_impl" : ["NMI","not-sleepable", 1],
        "bpf_obj_drop_impl" : ["NMI","not-sleepable", 1],
        "bpf_percpu_obj_drop_impl" : ["NMI","not-sleepable", 1],
        "bpf_refcount_acquire_impl" : ["NMI","not-sleepable", 1],
        "bpf_list_push_front_impl" : ["NMI","not-sleepable", 1],
        "bpf_list_push_back_impl" : ["NMI","not-sleepable", 1],
        "bpf_list_pop_front" : ["NMI","not-sleepable", 1],
        "bpf_list_pop_back" : ["NMI","not-sleepable", 1],
        "bpf_rbtree_remove" : ["NMI","not-sleepable", 1],
        "bpf_rbtree_add_impl" : ["NMI","not-sleepable", 1],
        "bpf_rbtree_first" : ["NMI","not-sleepable", 1],
        "bpf_task_acquire" : ["NMI","not-sleepable", 1],
        "bpf_task_release" : ["NMI","not-sleepable", 1],
        "bpf_task_release_dtor" : ["P","not-sleepable"],
        "bpf_cgroup_acquire" : ["NMI","not-sleepable", 1],
        "bpf_cgroup_release" : ["NMI","not-sleepable", 1],
        "bpf_cgroup_release_dtor" : ["P","not-sleepable"],
        "bpf_cgroup_ancestor" : ["NMI","not-sleepable", 1],
        "bpf_cgroup_from_id" : ["NMI","not-sleepable", 1],
        "bpf_task_under_cgroup" : ["NMI","not-sleepable", 1],
        "bpf_task_get_cgroup1" : ["NMI","not-sleepable", 1],
        "bpf_task_from_pid" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_slice" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_slice_rdwr" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_adjust" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_is_null" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_is_rdonly" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_size" : ["NMI","not-sleepable", 1],
        "bpf_dynptr_clone" : ["NMI","not-sleepable", 1],
        "bpf_cast_to_kern_ctx" : ["NMI","not-sleepable", 1],
        "bpf_rdonly_cast" : ["NMI","not-sleepable", 1],
        "bpf_rcu_read_lock" : ["NMI","not-sleepable", 1],
        "bpf_rcu_read_unlock" : ["NMI","not-sleepable", 1],
        "bpf_throw" : ["NMI","not-sleepable", 1],
        "bpf_map_sum_elem_count" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_vma_new" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_vma_next" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_vma_destroy" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_task_new" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_task_next" : ["NMI","not-sleepable", 1],
        "bpf_iter_css_task_destroy" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_new" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_next" : ["NMI","not-sleepable", 1],
        "bpf_iter_task_destroy" : ["NMI","not-sleepable", 1],
        "cgroup_rstat_updated" : ["NMI","not-sleepable", 1],
        "cgroup_rstat_flush" : ["P","sleepable",1],
        "crash_kexec" : ["NMI","not-sleepable", 1],
        "bpf_fentry_test1" : ["","sleepable"],
        "bpf_fentry_test9" : ["","not-sleepable"],
        "bpf_modify_return_test" : ["","not-sleepable"],
        "bpf_modify_return_test2" : ["","not-sleepable"],
        "bpf_kfunc_call_test_release" : ["NMI","not-sleepable", 1],
        "bpf_kfunc_call_test_release_dtor" : ["P","not-sleepable"],
        "bpf_kfunc_call_memb_release" : ["NMI","not-sleepable", 1],
        "bpf_kfunc_call_memb_release_dtor" : ["P","not-sleepable"],
        "bpf_dynptr_from_skb" : ["S","not-sleepable"],
        "bpf_dynptr_from_xdp" : ["S","not-sleepable"],
        "bpf_sock_addr_set_sun_path" : ["P","not-sleepable"],
        "bpf_sk_assign_tcp_reqsk" : ["S","not-sleepable"],
        "bpf_sock_destroy" : ["P","not-sleepable", 1],
        "bpf_xdp_metadata_rx_timestamp" : ["S","not-sleepable"],
        "bpf_xdp_metadata_rx_hash" : ["S","not-sleepable"],
        "bpf_xdp_metadata_rx_vlan_tag" : ["S","not-sleepable"],
        "bpf_skb_set_fou_encap" : ["S","not-sleepable"],
        "bpf_skb_get_fou_encap" : ["S","not-sleepable"],
        "bbr_min_tso_segs" : ["P","not-sleepable"],
        "bbr_cwnd_event" : ["P","not-sleepable"],
        "bbr_main" : ["P","not-sleepable"],
        "bbr_init" : ["P","not-sleepable"],
        "bbr_sndbuf_expand": ["P","not-sleepable"],
        "bbr_undo_cwnd": ["P","not-sleepable"],
        "bbr_ssthresh" : ["P","not-sleepable"],
        "bbr_set_state" : ["P","not-sleepable"],
        "tcp_slow_start" : ["P","not-sleepable"],
        "tcp_cong_avoid_ai" : ["P","not-sleepable"],
        "tcp_reno_cong_avoid" : ["P","not-sleepable"],
        "tcp_reno_ssthresh" : ["P","not-sleepable"],
        "tcp_reno_undo_cwnd" : ["P", "not-sleepable"],
        "cubictcp_init" : ["P","not-sleepable"],
        "cubictcp_cwnd_event" : ["P","not-sleepable"],
        "cubictcp_cong_avoid" : ["P","not-sleepable"],
        "cubictcp_recalc_ssthresh" : ["P","not-sleepable"],
        "cubictcp_state": ["P","not-sleepable"],
        "cubictcp_acked" : ["P","not-sleepable"],
        "dctcp_init" : ["P","not-sleepable"],
        "dctcp_ssthresh" : ["P","not-sleepable"],
        "dctcp_update_alpha" : ["P","not-sleepable"],
        "dctcp_state" : ["P","not-sleepable"],
        "dctcp_cwnd_event" : ["P","not-sleepable"],
        "dctcp_cwnd_undo" : ["P","not-sleepable"],
        "bpf_xdp_ct_alloc" : ["S","not-sleepable"],
        "bpf_xdp_ct_lookup" : ["S","not-sleepable"],
        "bpf_skb_ct_alloc" : ["S","not-sleepable"],
        "bpf_skb_ct_lookup" : ["S","not-sleepable"],
        "bpf_ct_insert_entry" : ["S","not-sleepable"],
        "bpf_ct_release" : ["S","not-sleepable"],
        "bpf_ct_set_timeout" : ["S","not-sleepable"],
        "bpf_ct_change_timeout" : ["S","not-sleepable"],
        "bpf_ct_set_status" : ["S","not-sleepable"],
        "bpf_ct_change_status" : ["S","not-sleepable"],
        "bpf_ct_set_nat_info" : ["S","not-sleepable"],
        "bpf_skb_get_xfrm_info" : ["S","not-sleepable"],
        "bpf_skb_set_xfrm_info" : ["S","not-sleepable"],
        "bpf_xdp_get_xfrm_state" : ["S","not-sleepable"],
        "bpf_xdp_xfrm_state_release" : ["S","not-sleepable"],
        "bpf_lookup_user_key": ["P", "sleepable"],
        "bpf_lookup_system_key": ["P", "not-sleepable"],
        "bpf_key_put": ["P", "not-sleepable"],
        "bpf_verify_pkcs7_signature": ["P", "sleepable"]
        }

kfunc_list_new = {
        "bpf_xdp_flow_lookup" : ["S", "not-sleepable"],
        "dctcp_react_to_loss" : ["P", "not-sleepable"],
        "dctcp_get_info": ["P", "not-sleepable"],

        "bpf_modify_return_test_tp": ["NMI", "not-sleepable", 1],

        "bpf_get_kmem_cache": ["NMI", "not-sleepable", 1],

        "bpf_session_is_return": ["NMI", "not-sleepable", 1],
        "bpf_session_cookie": ["NMI", "not-sleepable", 1],
        "bpf_send_signal_task": ["NMI", "not-sleepable", 1],

        "scx_bpf_select_cpu_dfl": ["P", "not-sleepable"],
        "scx_bpf_dsq_insert": ["P", "not-sleepable"],
        "scx_bpf_dispatch": ["P", "not-sleepable"],
        "scx_bpf_dsq_insert_vtime": ["P", "not-sleepable"],
        "scx_bpf_dispatch_vtime": ["P", "not-sleepable"],
        "scx_bpf_dispatch_nr_slots": ["P", "not-sleepable"],
        "scx_bpf_dispatch_cancel": ["P", "not-sleepable"],
        "scx_bpf_dsq_move_to_local": ["P", "not-sleepable"],
        "scx_bpf_consume": ["P", "not-sleepable"],
        "scx_bpf_dsq_move_set_slice": ["P", "not-sleepable"],
        "scx_bpf_dispatch_from_dsq_set_slice": ["P", "not-sleepable"],
        "scx_bpf_dsq_move_set_vtime": ["P", "not-sleepable"],
        "scx_bpf_dispatch_from_dsq_set_vtime": ["P", "not-sleepable"],
        "scx_bpf_dsq_move": ["P", "not-sleepable"],
        "scx_bpf_dispatch_from_dsq": ["P", "not-sleepable"],
        "scx_bpf_dsq_move_vtime": ["P", "not-sleepable"],
        "scx_bpf_dispatch_vtime_from_dsq": ["P", "not-sleepable"],
        "scx_bpf_reenqueue_local": ["P", "not-sleepable"],
        "scx_bpf_create_dsq": ["P", "not-sleepable"],
        "scx_bpf_kick_cpu": ["NMI", "not-sleepable", 1],
        "scx_bpf_dsq_nr_queued": ["NMI", "not-sleepable", 1],
        "scx_bpf_destroy_dsq": ["NMI", "not-sleepable", 1],
        "bpf_iter_scx_dsq_new": ["NMI", "not-sleepable", 1],
        "bpf_iter_scx_dsq_next": ["NMI", "not-sleepable", 1],
        "bpf_iter_scx_dsq_destroy": ["NMI", "not-sleepable", 1],
        "scx_bpf_exit_bstr": ["NMI", "not-sleepable", 1],
        "scx_bpf_error_bstr": ["NMI", "not-sleepable", 1],
        "scx_bpf_dump_bstr": ["NMI", "not-sleepable", 1],
        "scx_bpf_cpuperf_cap": ["NMI", "not-sleepable", 1],
        "scx_bpf_cpuperf_cur": ["NMI", "not-sleepable", 1],
        "scx_bpf_cpuperf_set": ["NMI", "not-sleepable", 1],
        "scx_bpf_nr_cpu_ids": ["NMI", "not-sleepable", 1],
        "scx_bpf_get_possible_cpumask": ["NMI", "not-sleepable", 1],
        "scx_bpf_get_online_cpumask": ["NMI", "not-sleepable", 1],
        "scx_bpf_put_cpumask": ["NMI", "not-sleepable", 1],
        "scx_bpf_get_idle_cpumask": ["NMI", "not-sleepable", 1],
        "scx_bpf_get_idle_smtmask": ["NMI", "not-sleepable", 1],
        "scx_bpf_put_idle_cpumask": ["NMI", "not-sleepable", 1],
        "scx_bpf_test_and_clear_cpu_idle": ["NMI", "not-sleepable", 1],
        "scx_bpf_pick_idle_cpu": ["NMI", "not-sleepable", 1],
        "scx_bpf_pick_any_cpu": ["NMI", "not-sleepable", 1],
        "scx_bpf_task_running": ["NMI", "not-sleepable", 1],
        "scx_bpf_task_cpu": ["NMI", "not-sleepable", 1],
        "scx_bpf_cpu_rq": ["NMI", "not-sleepable", 1],
        "scx_bpf_task_cgroup": ["NMI", "not-sleepable", 1],

        "bpf_iter_kmem_cache_new": ["NMI", "sleepable", 1],
        "bpf_iter_kmem_cache_next": ["NMI", "sleepable", 1],
        "bpf_iter_kmem_cache_destroy": ["NMI", "sleepable", 1],

        "hid_bpf_hw_output_report": ["P", "sleepable"],
        "hid_bpf_try_input_report": ["P", "sleepable"],
        "hid_bpf_input_report": ["P", "not-sleepable"],

        "bpf_get_task_exe_file": ["P", "not-sleepable"],
        "bpf_put_file": ["P", "not-sleepable"],
        "bpf_path_d_path": ["P", "not-sleepable"],
        "bpf_get_dentry_xattr": ["P", "sleepable"],
        "bpf_get_file_xattr": ["P", "sleepable"],

        "bpf_crypto_ctx_create": ["P", "sleepable"],
        "bpf_crypto_ctx_acquire": ["P", "not-sleepable"],
        "bpf_crypto_ctx_release": ["P", "not-sleepable"],
        "bpf_crypto_decrypt": ["S", "not-sleepable"],
        "bpf_crypto_encrypt": ["S", "not-sleepable"],
        "bpf_task_from_vpid": ["NMI", "not-sleepable", 1],
        "bpf_wq_init": ["NMI", "not-sleepable", 1],
        "bpf_wq_start": ["NMI", "not-sleepable", 1],
        "bpf_wq_set_callback_impl": ["NMI", "not-sleepable", 1],
        "bpf_preempt_disable": ["NMI", "not-sleepable", 1],
        "bpf_preempt_enable": ["NMI", "not-sleepable", 1],
        "bpf_iter_bits_new": ["NMI", "not-sleepable", 1],
        "bpf_iter_bits_next": ["NMI", "not-sleepable", 1],
        "bpf_iter_bits_destroy": ["NMI", "not-sleepable", 1],
        "bpf_copy_from_user_str": ["NMI", "sleepable", 1],
}



function_lists = [function_list_array, function_list_percpu_array, function_list_prog_array, function_list_perf_event_array, 
        function_list_cgroup_array, function_list_array_of_maps, function_list_bloom_filter, function_list_htab, function_list_htab_lru, 
        function_list_htab_percpu, function_list_htab_lru_percpu , function_list_htab_of_maps, function_list_stack_trace, function_list_trie,
        function_list_dev, function_list_dev_hash, function_list_sock, function_list_sock_hash, function_list_cpu, function_list_xsk,
        function_list_reuseport_array, function_list_stack, function_list_queue, function_list_sk_storage, function_list_struct_ops, function_list_ringbuf,
        function_list_inode_storage, function_list_task_storage, function_list_user_ringbuf, function_list_cgrp_storage, function_list_arena, kfunc_list,
        kfunc_list_new]
node_list = {}


def get_nodes(graph_file_name):
    graph_file = open(graph_file_name, 'r')

    function_list_helpers = helper_context();
    function_lists.append(function_list_helpers)


    for list in function_lists:
        for key in list:
            flag = False
            while True:
                line = graph_file.readline()
                if not line:
                    break
                #if key in line and key==line[line.index("fun:")+5 : line.rindex("\\")]: ##for SVF gen callgraphs
                if key in line and key==line[line.index("fun:")+5 : line.rindex("}")]:  ##for mlta gen callgraphs
                    flag = True
                    #node_list[line[1:19]]=list[key] ##for SVF gen callgraphs
                    node_list[line[:line.index("[")-1]]=list[key] ##for mlta gen callgraphs
            #if flag==False:
                #print("Node matching "+key+" not found.")
            graph_file.seek(0)
            


    json_object = json.dumps(node_list)

    with open('nodes.json', "w") as outfile:
        outfile.write(json_object)

    json_object2 = json.dumps(function_lists)

    #with open('../poc/specs.json', "w") as outfile:
    #    outfile.write(json_object2)

