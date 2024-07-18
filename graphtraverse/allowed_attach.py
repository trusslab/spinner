import json
import networkx as nx

function_list_allowed = {
        "bpf_ima_inode_hash" : ["kernel/bpf/bpf_lsm.c", "bpf_ima_inode_hash_allowed", "context", {}],
        "bpf_ima_file_hash" : ["kernel/bpf/bpf_lsm.c","bpf_ima_inode_hash_allowed", "context", {}],
        "bpf_sk_storage_get_tracing" : ["net/core/bpf_sk_storage.c","bpf_sk_storage_tracing_allowed", "context", {}],
        "bpf_sk_storage_delete_tracing" : ["net/core/bpf_sk_storage.c","bpf_sk_storage_tracing_allowed", "context", {}],
        "bpf_d_path" : ["kernel/trace/bpf_trace.c","bpf_d_path_allowed", "context", {}],
        }

def find_allowed_function():
    for key in function_list_allowed:
        
        source_file_name = kernel_path+function_list_allowed[key][0]
        source_file = open(source_file_name, 'r')
        search_allowed=False
    
        while True:
            line = source_file.readline()
            if not line:
                break
            if key+"_proto" in line:
                search_allowed = True
            if "};" in line and search_allowed==True:
                search_allowed = False
            if ".allowed" in line and search_allowed==True:
                #print(line)
                function_list_allowed[key][1] = line[line.index("=")+2:line.rindex(",")]
                #print(function_list_allowed[key][1])
        source_file.seek(0)
        source_file.close()

def find_allowed_hooks():
    source_file_name = kernel_path+function_list_allowed["bpf_ima_inode_hash"][0]
    source_file = open(source_file_name, 'r')
    add_hooks = False
    while True:
            line = source_file.readline()
            if not line:
                break
            if "BTF_SET_START(sleepable_lsm_hooks)" in line:
                add_hooks = True
            if "BTF_SET_END(sleepable_lsm_hooks)" in line:
                add_hooks = False
            if "BTF_ID" in line and add_hooks==True:
                function_list_allowed["bpf_ima_inode_hash"][3][line[line.index("func")+6:line.rindex(")")]] = ["NodeID", []]
                function_list_allowed["bpf_ima_file_hash"][3][line[line.index("func")+6:line.rindex(")")]] = ["NodeID", []]
                function_list_allowed["bpf_d_path"][3][line[line.index("func")+6:line.rindex(")")]] = ["NodeID", []]


    source_file.seek(0)
    source_file.close()

    source_file_name = kernel_path+function_list_allowed["bpf_d_path"][0]
    source_file = open(source_file_name, 'r')
    add_hooks = False
    while True:
            line = source_file.readline()
            if not line:
                break
            if "BTF_SET_START(btf_allowlist_d_path)" in line:
                add_hooks = True
            if "BTF_SET_END(btf_allowlist_d_path)" in line:
                add_hooks = False
            if "BTF_ID" in line and add_hooks==True:
                function_list_allowed["bpf_d_path"][3][line[line.index("func")+6:line.rindex(")")]] = ["NodeID", []]
    source_file.seek(0)
    source_file.close()

def find_hook_nodes(graph_file):
    for key in function_list_allowed:
        for hook in function_list_allowed[key][3]:
            flag = False
            while True:
                line = graph_file.readline()
                #print(line)
                if not line:
                    break
                if hook in line and hook==line[line.index("fun:")+5 : line.rindex("\\")]:
                    flag = True
                    function_list_allowed[key][3][hook][0] =  line[1:19] 
            #if flag==False:
                #print("Node matching "+hook+" not found.")
            
            graph_file.seek(0)


def trace_hooks(graph_file, callgraph):
    no_pred = "__traceiter_initcall_finish"

    for key in function_list_allowed:
        for hook in function_list_allowed[key][3]:
            hook_details = function_list_allowed[key][3][hook]
            if hook_details[0] == "NodeID":
                continue
            pred = []
            pred.append(hook_details[0])
            pred_names = []
            pred_label = callgraph._node[pred[0]]["label"]
            pred_fun_name = pred_label[pred_label.index("fun:")+5 : pred_label.rindex("\\")]
            
            for predecessor in pred:
                while True:
                    line = graph_file.readline()
                    if not line:
                        break
                    if predecessor in line and predecessor!=line[1:19]:
                        caller_node = line[1:19]
                        caller_label = callgraph._node[caller_node]["label"]
                        caller_name = caller_label[caller_label.index("fun:")+5 : caller_label.rindex("\\")]
                        if caller_node not in pred:
                            pred.append(caller_node)
                            pred_names.append(caller_name)
                            print(pred_fun_name + " : "+caller_name)

                graph_file.seek(0)
            function_list_allowed[key][3][hook][1] = pred
    print(function_list_allowed["bpf_d_path"][3]["vfs_truncate"][1])
                    



graph_file_name = input("Enter graph file to read: ")
graph_file = open(graph_file_name, 'r')

json_file_name = input("Enter .json file name to write to: ")
kernel_path = "/home/priya/linux-6.6.4/"
callgraph_linux = nx.drawing.nx_agraph.read_dot(graph_file_name)

find_allowed_function()
find_allowed_hooks()
find_hook_nodes(graph_file) 
trace_hooks(graph_file, callgraph_linux)

json_object = json.dumps(function_list_allowed)

with open(json_file_name, "w") as outfile:
    outfile.write(json_object)

graph_file.close()
