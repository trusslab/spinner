import networkx as nx
import json
from graph_nodes import get_nodes

callgraph_file_name = "../mlta/callgraph6.9.dot"
node_file_name = "nodes.json"
get_nodes(callgraph_file_name)

callgraph_linux = nx.drawing.nx_agraph.read_dot(callgraph_file_name)

SVF = 0 

def get_precur_functions():
    precur_file = open("../fptests/output/precur.txt", "r")
    precur_funcs = []
    while True:
        line = precur_file.readline()
        if not line:
            break
        precur_funcs.append(line.split()[0])
    return precur_funcs

def get_name(node):
    if not node:
        return ""  
    label = node["label"]
    if SVF==1:
        fun_name = label[label.index("fun:")+5 : label.rindex("\\")]
    else:
        fun_name = label[label.index("fun:")+5 : label.rindex("}")]
    return fun_name


def check_S(child_name):
    if child_name=="_raw_spin_lock":
        return True
    elif child_name=="local_lock":
        return True
    elif "local_lock." in child_name:
        return True
    return False

def check_H(child_name):
    if child_name=="_raw_spin_lock":
        return True
    elif child_name=="_raw_spin_lock_bh":
        return True
    elif child_name=="local_lock":
        return True
    elif "local_lock." in child_name:
        return True
    return False

def check_NMI(child_name):
    nmi_function_list = ["_raw_spin_lock", "_raw_spin_lock_bh", "_raw_spin_lock_irq", "_raw_spin_lock_irqsave", 
            "local_lock", "local_lock_irq", "local_lock_irqsave" ]
    if child_name in nmi_function_list:
        return True
    if "local_lock." in child_name or "local_lock_irqsave." in child_name or  "local_lock_irq." in child_name:
        return True
    return False

def check_nested_lock(child_name):
    lock_list = ["_raw_spin_lock", "_raw_spin_lock_bh", "_raw_spin_lock_irq", "_raw_spin_lock_irqsave"]
    if child_name in lock_list:
        return True
    return False

skiplist = [
        #doesn't make sense to search after these functions
        'panic',
        'machine_crash_shutdown', 
        'crash_kexec', 
        'start_kernel', 
        'emergency_restart', 
        #debugging functions
        'kdb_gdb_state_pass', 
        'gdbstub_state',
        'vkdb_printf',  
        'start_report',
        'lock_acquire',
        'register_lock_class',
        'show_stack',
        'kernel_text_address',
        'kasan_save_stack',
        '__kasan_record_aux_stack',
        '__kfence_free',
        #printing functions
        'vprintk', 
        'vprintk_emit',
        #other
        'btf_parse_vmlinux', #only called in process context to generate btf info for the first time
        'migrate_enable', #bpf programs run with preemption and migration disabled so __set_cpus_allowed_ptr is never called
        #don't want to deal with RCU
        'rcu_read_unlock_special',
        'kvfree_call_rcu',
        #miscellaneous
        '__queue_work',
        '__ratelimit', 
        '___ratelimit',
        'check_critical_timing',
        '__queue_delayed_work',
        'get_random_bytes',
        'try_to_wake_up',
        '_get_random_bytes',
        'dequeue_task', 
        'mod_timer', 
        'lock_acquire', 
        'rwsem_wake',
        'kfree',
        'get_random_u8',
        ]

def dfs_path(callgraph, source, end_name, parent_map):
    path = []
    curr = end_name
    counter = 0
    while curr in parent_map:
        if curr!=None:
            if curr in path:
                index = path.index(curr)
                path=path[:index]
            if curr in skiplist:
                return []
            path.append(curr)

        curr = parent_map[curr]
        counter+=1
        if counter > 50:
            break
    path = path[::-1]
    for func in path:
        if func in skiplist:
            return []
    for children in callgraph.neighbors(source):
        if path[0]==get_name(callgraph._node[children]):
            return path
    for i in range(len(path)):
        for children in callgraph.neighbors(source):
            if path[i]==get_name(callgraph._node[children]):
                path = path[i:]
                return path
    return []

def dfs_nx(callgraph, source, max_context, recur):
    nodes = [source]
    depth_limit = 50
    parent_map = {}
    reports = []
    if source in callgraph:
        source_fun_name = get_name(callgraph._node[source])
    else:
        return

    get_children = (
        callgraph.neighbors 
        )

    visited = set()
    for start in nodes:
        if start in visited:
            continue
        visited.add(start)
        stack = [(start, get_children(start))]
        depth_now = 1

        lock_stack = []
        path = ""

        while len(stack)!=0:
            parent, children = stack.pop()
            parent_fun_name = get_name(callgraph._node[parent])

            for child in children:
                warning = [False, False]
                child_fun_name = get_name(callgraph._node[child])
                parent_map[child_fun_name] = parent_fun_name
                
                if source_fun_name in get_precur_functions():
                    if (check_nested_lock(child_fun_name)):
                        warning[1] = True

                if recur:
                    if (check_nested_lock(child_fun_name)):
                        warning[1] = True

                if max_context=="S":
                    if (check_S(child_fun_name)):
                        warning[0] = True
                elif max_context=="H":
                    if (check_H(child_fun_name)):
                        warning[0] = True
                elif max_context == "NMI":
                    if (check_NMI(child_fun_name)):
                        warning[0] = True
                
                if warning[0]:
                    path = dfs_path(callgraph, source, child_fun_name, parent_map)
                    if path!=[]:
                        report = "WARNING: "+source_fun_name+" used "+child_fun_name+"\n"+', '.join(path)
                        if report not in reports:
                            reports.append(report)

                if warning[1]:
                     path = dfs_path(callgraph, source, child_fun_name, parent_map)
                     if path!=[]:
                        report = "WARNING: "+source_fun_name+" used "+child_fun_name+" nested issue" + "\n"+', '.join(path)
                        if report not in reports:
                            reports.append(report)
                          
                if child not in visited:
                    visited.add(child)
                    if depth_now < depth_limit:
                        stack.append((child, get_children(child)))                       
                        depth_now += 1
            else: 
                depth_now -= 1
    
    for i in range(len(reports)):
        print(reports[i], "\n")
    
with open(node_file_name) as json_file:
    function_list_json = json.load(json_file)
    for key in function_list_json:
        recur = 0
        if len(function_list_json[key])==3:
            recur = 1
        if function_list_json[key][1]!="sleepable":
            dfs_nx(callgraph_linux, key, function_list_json[key][0], recur)
    
