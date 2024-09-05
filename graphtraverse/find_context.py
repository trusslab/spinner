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
        
def get_ancestors(graph, SVF):
    if SVF==True:
        for key in run_functions:
            if not run_functions[key]:
                print(key)
                continue
            node = run_functions[key][0]
            if not node:
                print(key)
                continue

            ancestors = nx.ancestors(graph, node)
            pred = []
            pred.append(node)
            pred_names = []
            pred_names.append(get_name(graph._node[pred[0]], SVF))
            for ancestor in ancestors:
                pred.append(ancestor)
                pred_names.append(get_name(graph._node[ancestor], SVF))
            run_functions[key].append(pred)
            run_functions[key].append(pred_names)
    else:
        for key in mlta_run_functions:
            if not mlta_run_functions[key]:
                print(key)
                continue
            node = mlta_run_functions[key][0]
            if not node:
                print(key)
                continue

            ancestors = nx.ancestors(graph, node)
            pred = []
            pred.append(node)
            pred_names = []
            pred_names.append(get_name(graph._node[pred[0]], SVF))
            for ancestor in ancestors:
                pred.append(ancestor)
                pred_names.append(get_name(graph._node[ancestor], SVF))
            mlta_run_functions[key].append(pred)
            mlta_run_functions[key].append(pred_names)


def get_possibilities(SVF):
    possibilities = {}
    softirq_funcs = ['tasklet_action_common', 'net_tx_action', 'net_rx_action', 'run_timer_softirq']
    if SVF==True:
        for function in run_functions:
            process = []
            softirq = []
            hardirq = []
            nmi = []
            possibilities[function] = [process, softirq, hardirq, nmi]
            if run_functions[function] == []:
                continue
            for pred in run_functions[function][2]:
                if pred.startswith("__do_sys") or pred.startswith("__ia32_sys"):
                    possibilities[function][0].append(pred)
                elif pred in softirq_funcs:
                    possibilities[function][1].append(pred)
                elif pred == "__handle_irq_event_percpu":
                    possibilities[function][2].append(pred)
                elif pred == "default_do_nmi":
                    possibilities[function][3].append(pred)

    else:
        for function in mlta_run_functions:
            process = []
            softirq = []
            hardirq = []
            nmi = []
            possibilities[function] = [process, softirq, hardirq, nmi]
            if mlta_run_functions[function] == []:
                continue
            for pred in mlta_run_functions[function][2]:
                if pred.startswith("__do_sys") or pred.startswith("__ia32_sys"):
                    possibilities[function][0].append(pred)
                elif pred in softirq_funcs:
                    possibilities[function][1].append(pred)
                elif pred == "__handle_irq_event_percpu":
                    possibilities[function][2].append(pred)
                elif pred == "default_do_nmi":
                    possibilities[function][3].append(pred)

    return possibilities


def SVF_main():
    SVF_graph_file_name = "/home/priya/callgraphs/callgraph_linux_VFSWPA.dot"
    SVF_graph_file = open(SVF_graph_file_name, 'r')
    json_file_name = input("Enter .json file name to write to: ")
    kernel_path = "/home/priya/linux-6.9bc/"
    SVF_callgraph_linux = nx.drawing.nx_agraph.read_dot(SVF_graph_file_name)
    find_run_nodes(SVF_graph_file, True)
    #SVF_trace_run_functions(SVF_graph_file, SVF_callgraph_linux)
    get_ancestors(SVF_callgraph_linux, True)
    json_object_1 = json.dumps(run_functions, indent = 5)
    with open(json_file_name, "w") as outfile:
        outfile.write(json_object_1)

    possibilities = get_possibilities(True)
    json_object_poss = json.dumps(possibilities, indent = 5)
    with open(json_file_name, "a") as outfile:
        outfile.write(json_object_poss)

    SVF_graph_file.close()


def mlta_main():
    mlta_graph_file_name = "/home/priya/callgraphs/callgraph_mlta_69fulldirect.dot"
    mlta_graph_file = open(mlta_graph_file_name, 'r')

    json_file_name = input("Enter .json file name to write to: ")
    kernel_path = "/home/priya/linux-6.9bc/"
    mlta_callgraph_linux = nx.drawing.nx_agraph.read_dot(mlta_graph_file_name)
    find_run_nodes(mlta_graph_file, False)
    #mlta_trace_run_functions(mlta_graph_file, mlta_callgraph_linux)
    get_ancestors(mlta_callgraph_linux, False)
    json_object_2 = json.dumps(mlta_run_functions, indent = 5)

    with open(json_file_name, "w") as outfile:
        outfile.write(json_object_2)

    possibilities = get_possibilities(False)
    json_object_poss = json.dumps(possibilities, indent = 5)
    with open(json_file_name, "a") as outfile:
        outfile.write(json_object_poss)
    mlta_graph_file.close()


if __name__ == "__main__":
    mlta_main()
