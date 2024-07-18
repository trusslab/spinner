import json
import networkx as nx
import copy

run_functions = {
        "bpf_struct_ops_test_run" : [],
        "__cgroup_bpf_run_lsm_sock" : [],
        "__cgroup_bpf_run_lsm_socket" : [],
        "__cgroup_bpf_run_lsm_current" : [],
        "__cgroup_bpf_run_filter_skb" : [],
        "__cgroup_bpf_run_filter_sk" : [],
        "__cgroup_bpf_run_filter_sock_addr" : [],
        "__cgroup_bpf_run_filter_sock_ops" : [],
        "__cgroup_bpf_check_dev_permission" : [],
        "__cgroup_bpf_run_filter_sysctl" : [],
        "__cgroup_bpf_run_filter_setsockopt" : [],
        "__cgroup_bpf_run_filter_getsockopt" : [],
        "__cgroup_bpf_run_filter_getsockopt_kern" : [],
        "sk_filter_trim_cap" : [],
        "trace_call_bpf" : [],
        "kprobe_multi_link_prog_run" : [],
        "uprobe_prog_run" : [],
        "__uprobe_perf_func" : [],
        "cls_bpf_classify" : [],
        "tcf_bpf_act" : [],
        "bpf_prog_run_xdp" : [],
        "cpu_map_bpf_prog_run_xdp" : [],
        "bpf_prog_run_generic_xdp" : [],
        "run_lwt_bpf" : [],
        "kcm_parse_func_strparser" : [],
        "sk_psock_tls_strp_read" : [],
        "sk_psock_strp_read" : [],
        "sk_psock_strp_parse" : [],
        "sk_psock_verdict_recv" : [],
        "sk_psock_msg_verdict" : [],
        "input_action_end_bpf" : [],
        "lirc_bpf_run" : [],
        "bpf_run_sk_reuseport" : [],
        "run_bpf_filter" : [],
        "bpf_flow_dissect" : [],
        "__bpf_trace_run" : [],
        "bpf_trace_run" : [],
        "bpf_struct_ops_test_run" : [],
        "bpf_sk_lookup_run_v4" : [],
        "bpf_sk_lookup_run_v6" : [],
        "bpf_mt" : [],
        "bpf_mt_v1" : [],
        "nf_hook_run_bpf" : [],
        "bpf_prog_run" : [],
}

mlta_run_functions = copy.deepcopy(run_functions)

def get_name(node, SVF):
    if not node:
        return ""
    label = node["label"]
    if SVF==True:
        fun_name = label[label.index("fun:")+5 : label.rindex("\\")]
    else:
        fun_name = label[label.index("fun:")+5 : label.rindex("}")]
    return fun_name


def find_run_nodes(graph_file, SVF):
    for key in run_functions:
        flag = False
        while True:
            line = graph_file.readline()
            #print(line)
            if not line:
                break
            if "fun:" in line:
                if SVF==True:
                    if key in line and key==line[line.index("fun:")+5 : line.rindex("\\")]:
                        flag = True
                        run_functions[key].append(line[1:19])
                else:
                    if key in line and key==line[line.index("fun:")+5 : line.rindex("}")]:
                        flag = True
                        mlta_run_functions[key].append(line[:line.index("[")-1])
        if flag==False:
            print("Node matching "+key+" not found.")

        graph_file.seek(0)

def SVF_trace_run_functions(graph_file, callgraph):
    no_pred = "__traceiter_initcall_finish"

    for key in run_functions:
        if not run_functions[key]:
            print(key)
            continue
        node = run_functions[key][0]
        if not node:
            print(key)
            continue
        pred = []
        pred.append(node)
        pred_names = []
        pred_fun_name = get_name(callgraph._node[pred[0]], True)
        pred_names.append(pred_fun_name)
        
        for predecessor in pred:
            while True:
                line = graph_file.readline()
                if not line:
                    break
                if predecessor in line and predecessor!=line[1:19]:
                    caller_node = line[1:19]
                    caller_name = get_name(callgraph._node[caller_node], True)
                    if caller_node not in pred:
                        pred.append(caller_node)
                        pred_names.append(caller_name)
                        #print(pred_fun_name + " : "+caller_name)

            graph_file.seek(0)
        run_functions[key].append(pred)
        run_functions[key].append(pred_names)
        #print(run_functions[key])

def mlta_trace_run_functions(graph_file, callgraph):
    no_pred = "__traceiter_initcall_finish"

    for key in mlta_run_functions:
        if not mlta_run_functions[key]:
            print(key)
            continue
        node = mlta_run_functions[key][0]
        if not node:
            print(key)
            continue
        pred = []
        pred.append(node)
        pred_names = []
        pred_fun_name = get_name(callgraph._node[pred[0]], False)
        pred_names.append(pred_fun_name)

        for predecessor in pred:
            while True:
                line = graph_file.readline()
                if not line:
                    break
                if predecessor in line and predecessor!=line[:line.index("[")-1]:
                    caller_node = line[:line.index("-")-1]
                    caller_name = get_name(callgraph._node[caller_node], False)
                    if caller_node not in pred:
                        pred.append(caller_node)
                        pred_names.append(caller_name)
                        #print(pred_fun_name + " : "+caller_name)

            graph_file.seek(0)
        mlta_run_functions[key].append(pred)
        mlta_run_functions[key].append(pred_names)
        #print(run_functions[key])


SVF_graph_file_name = input("Enter SVF graph file to read: ")
SVF_graph_file = open(SVF_graph_file_name, 'r')

#mlta_graph_file_name = "callgraph_mlta_69fulldirect.dot"
#mlta_graph_file = open(mlta_graph_file_name, 'r')

json_file_name = input("Enter .json file name to write to: ")
kernel_path = "/home/priya/linux-6.9bc/"
SVF_callgraph_linux = nx.drawing.nx_agraph.read_dot(SVF_graph_file_name)
#mlta_callgraph_linux = nx.drawing.nx_agraph.read_dot(mlta_graph_file_name)


find_run_nodes(SVF_graph_file, True)
#find_run_nodes(mlta_graph_file, False)
SVF_trace_run_functions(SVF_graph_file, SVF_callgraph_linux)
#mlta_trace_run_functions(mlta_graph_file, mlta_callgraph_linux)


json_object_1 = json.dumps(run_functions, indent = 5)
#json_object_2 = json.dumps(mlta_run_functions, indent = 5)

with open(json_file_name, "w") as outfile:
    outfile.write(json_object_1)
    #outfile.write(json_object_2)

SVF_graph_file.close()
#mlta_graph_file.close()

