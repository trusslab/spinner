import networkx as nx
import json

callgraph_file_name = input("Enter .dot file name:")
node_file_name = input("Enter .json file name:")
callgraph_linux = nx.drawing.nx_agraph.read_dot(callgraph_file_name)
print("networkx graph created")

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


def check_S(source_name, child_name):
    if child_name=="_raw_spin_lock":
        return True
    elif child_name=="local_lock":
        return True
    return False

def check_H(source_name, child_name):
    if child_name=="_raw_spin_lock":
        return True
    elif child_name=="_raw_spin_lock_bh":
        return True
    elif child_name=="local_lock":
        return True
    elif child_name=="local_lock_bh":
        return True
    return False

def check_NMI(source_name, child_name):
    nmi_function_list = ["_raw_spin_lock", "_raw_spin_lock_bh", "_raw_spin_lock_irq", "_raw_spin_lock_irqsave", 
            "local_lock", "local_lock_bh", "local_lock_irq", "local_lock_irqsave" ]
    if child_name in nmi_function_list:
        return True
    else:
        return False

def check_synchronize_rcu(source_name, child_name):
    synchronize_rcu_list = ["synchronize_rcu", "synchronize_rcu_expedited", "__synchronize_srcu", "synchronize_srcu", "synchronize_srcu_expedited"]
    if child_name in synchronize_rcu_list:     
         return True
    return False

def check_sleeping_locks(source_name, child_name):
    sleeping_locks_list = ["down", "__down", "down_interruptible", "__down_interruptible", "down_killable", "__down_killable", "down_trylock", 
            "down_timeout", "__down_timeout", "__down_common","__emit_semaphore_wait", "semaphore_notify", "bad_area_nosemaphore",
            "__bad_area_nosemaphore", "rt_mutex_unlock", "rt_mutex_slowunlock", "rt_mutex_trylock", "rt_mutex_slowtrylock", "try_to_take_rt_mutex",
            "rt_mutex_lock_killable", "rt_mutex_slowlock", "__rt_mutex_slowlock", "task_blocks_on_rt_mutex", "rt_mutex_slowlock_block",
            "rt_mutex_handle_deadlock", "rt_mutex_adjust_prio_chain", "rt_mutex_lock_interruptible", "rt_mutex_lock", "rt_mutex_base_init",
            "__rt_mutex_init", "rt_mutex_futex_trylock", "__rt_mutex_futex_trylock", "__rt_mutex_futex_unlock", "rt_mutex_futex_unlock", 
            "rt_mutex_postunlock", "rt_mutex_init_proxy_locked", "rt_mutex_proxy_unlock", "__rt_mutex_start_proxy_lock", "rt_mutex_start_proxy_lock",
            "rt_mutex_wait_proxy_lock", "rt_mutex_cleanup_proxy_lock", "rt_mutex_adjust_pi", "hugetlb_fault_mutex_hash", "epoll_mutex_lock",
            "refcount_dec_and_mutex_lock", "drm_dev_needs_global_mutex", "__drmm_mutex_release", "i915_gem_shrinker_taints_mutex", "regmap_lock_mutex",
            "regmap_unlock_mutex", "rt_mutex_setprio", "ww_mutex_unlock", "__mutex_unlock_slowpath", "ww_mutex_trylock", "__ww_mutex_check_waiters",
            "ww_mutex_lock_interruptible", "__ww_mutex_lock_interruptible_slowpath", "__ww_mutex_lock", "mutex_spin_on_owner", "ww_mutex_lock",
            "__ww_mutex_lock_slowpath", "mutex_unlock", "mutex_trylock", "mutex_lock_killable", "__mutex_lock_killable_slowpath", "__mutex_lock",
            "mutex_lock_io", "__mutex_lock_slowpath", "mutex_lock_interruptible", "__mutex_lock_interruptible_slowpath", "mutex_lock", "mutex_is_locked",
            "atomic_dec_and_mutex_lock", "__mutex_init"]
    if child_name in sleeping_locks_list:
        return True
    else:
        return False


def check_sleeping_functions(source_name, child_name):
    sleeping_function_list = ["__might_sleep", "might_sleep", "schedule", "__schedule", "schedule_timeout", "__might_resched", "might_sleep_if", 
            "sched_annotate_sleep", "msleep", "usleep_range_state", "usleep_range", "usleep_idle_range", "ssleep", "fsleep"]
    if child_name in sleeping_function_list:
        return True
    else:
        return False

lock_dict = {'_raw_spin_lock': '_raw_spin_unlock', '_raw_spin_lock_bh': '_raw_spin_unlock_bh', '_raw_spin_lock_irq': '_raw_spin_unlock_irq',
        '_raw_spin_lock_irqsave': '_raw_spin_unlock_irqrestore' }

skiplist = ['panic', 'machine_crash_shutdown', 'crash_kexec', 'start_kernel', 'emergency_restart', '__queue_work', 'kdb_gdb_state_pass', 'gdbstub_state',
        'vprintk', 'vkdb_printf','__ratelimit', '___ratelimit', 'try_to_wake_up', 'vprintk_emit', '__queue_delayed_work', 'get_random_bytes', 
        '_get_random_bytes', 'show_stack', 'kernel_text_address',  'kvfree_call_rcu', 'kvfree', 'kfree', 'vfree', 'migrate_enable', 'rcu_read_unlock.46470', 
        'rcu_read_unlock.24024']

def dfs_path(callgraph, source, end, parent_map):
    path = []
    curr = end
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
    return path

def dfs_nx(callgraph, source, max_context):
    nodes = [source]
    depth_limit = 50
    parent_map = {}
    source_fun_name = get_name(callgraph._node[source])

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
            irq_disabled = 0
            
            for child in children:
                warning = 0
                child_fun_name = get_name(callgraph._node[child])
                parent_map[child_fun_name] = parent_fun_name
               
                if source_fun_name in get_precur_functions():
                    if (check_NMI(source_fun_name, child_fun_name)):
                        warning = 2

                if "map" in source_fun_name:
                    if (check_NMI(source_fun_name, child_fun_name)):
                        warning = 2

                if max_context=="S":
                    #if not irq_disabled:
                    if (check_S(source_fun_name, child_fun_name)):
                        warning = 1
                    if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                        warning = 1
                    if(check_sleeping_functions(source_fun_name, child_fun_name)):
                        warning = 1
                    if check_sleeping_locks(source_fun_name, child_fun_name):
                        warning = 1

                elif max_context=="H":
                    #if not irq_disabled:
                    if (check_H(source_fun_name, child_fun_name)):
                        warning = 1
                    if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                        warning = 1
                    if (check_sleeping_functions(source_fun_name, child_fun_name)):
                        warning = 1
                    if (check_sleeping_locks(source_fun_name, child_fun_name)):
                        warning = 1

                elif max_context == "NMI":
                    if (check_NMI(source_fun_name, child_fun_name)):
                        warning = 1
                    if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                        warning = 1
                    if (check_sleeping_functions(source_fun_name, child_fun_name)):
                        warning = 1
                    if (check_sleeping_locks(source_fun_name, child_fun_name)):
                        warning = 1
                
                if warning == 1:
                    path = dfs_path(callgraph, source_fun_name, child_fun_name, parent_map)
                    if path!=[]:
                        print("WARNING: "+source_fun_name+" used "+child_fun_name)
                        print(path)

                if warning == 2:
                     path = dfs_path(callgraph, source_fun_name, child_fun_name, parent_map)
                     if path!=[]:
                        print("WARNING: "+source_fun_name+" used "+child_fun_name+" recursive issue")
                        print(path)
                
                if child not in visited:
                    visited.add(child)
                    if depth_now < depth_limit:
                        stack.append((child, get_children(child)))                       
                        depth_now += 1
            else: 
                depth_now -= 1

def bfs_path (callgraph, source, end):
    queue = []
    queue.append([source])
    source_fun_name = get_name(callgraph._node[source])
    
    queue_readable = []
    queue_readable.append([source_fun_name])
    while queue:
        path=queue.pop(0)
        path_readable = queue_readable.pop(0)
        node = path[-1]
        if node==end:
            return path_readable
        for neighbor in callgraph.neighbors(node):
            neighbor_fun_name = get_name(callgraph._node[neighbor])
            new_path = list(path)
            new_path_readable = list(path_readable)
            new_path.append(neighbor)
            new_path_readable.append(neighbor_fun_name)
            queue.append(new_path)
            queue_readable.append(new_path_readable)


def bfs (callgraph, source, max_context):
    source_fun_name = get_name(callgraph._node[source])
    path= []
    flag = 0
    if source_fun_name == "sock_hash_delete_elem":
        flag = 1
    depth_limit = 20 
    neighbors = callgraph.neighbors
    seen = {source}
    n = len(callgraph)
    depth = 1 
    next_parents_children = [(source, neighbors(source))]
    while next_parents_children and depth<depth_limit:
        this_parents_children = next_parents_children
        next_parents_children = []
        for parent, children in this_parents_children:

            parent_fun_name = get_name(callgraph._node[parent])
           
            path.append(parent_fun_name)

            for child in children:
                if child not in seen:
                    child_fun_name = get_name(callgraph._node[child])

                    skip_list = ['vprintk', '_get_random_bytes', '_printk', 'panic', '__alloc', '__alloc_pages', 'kvfree_call_rcu', 'call_rcu'
                            , 'rcu_read_unlock_special']
                    if child_fun_name in skip_list:
                        return

                    if flag==1:
                        print(child_fun_name)

                    if max_context=="S":
                        if (check_S(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        
                        if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        if(check_sleeping_functions(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        if check_sleeping_locks(source_fun_name, child_fun_name):
                            print(bfs_path(callgraph, source, child))
                    
                    if max_context=="H":
                        if (check_H(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                            #print(path)
                        
                        if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                            #if flag==1:
                                #print(path)

                        if (check_sleeping_functions(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                            #if flag==1:
                                #print(path)
                        if (check_sleeping_locks(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                            #if flag==1:
                                #print(path)
                        
                    if max_context=="NMI":
                        if (check_NMI(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        
                        if(check_synchronize_rcu(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        if(check_sleeping_functions(source_fun_name, child_fun_name)):
                            print(bfs_path(callgraph, source, child))
                        if check_sleeping_locks(source_fun_name, child_fun_name):
                            print(bfs_path(callgraph, source, child))
                        
                    seen.add(child)
                    next_parents_children.append((child, neighbors(child)))
            if len(seen) == n:
                return 
        depth+=1


#label = callgraph._node["Node0x55e211e202f0"]["label"]
#fun_name = label[label.index("fun:")+5 : label.rindex("\\")]
#print("calling dfs")

with open(node_file_name) as json_file:
    function_list_json = json.load(json_file)
    #print(function_list_json)

    #dfs_nx(callgraph_linux, "Node0x563e8ef2ecf0", function_list_json["Node0x563e8ef2ecf0"])
     
    for key in function_list_json:
        #if get_name(callgraph_linux._node[key])=="trie_delete_elem":
        dfs_nx(callgraph_linux, key, function_list_json[key])
    
       
#print(fun_name)
