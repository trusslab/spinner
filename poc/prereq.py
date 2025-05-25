import json
import re
import sys
from find_attach import find_attach
from find_attach import convert_prog_type
from find_attach import complete_attach

def read_kernel_path():
    with open("config.conf", 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('KERNEL_DIR='):
                _, value = line.split('=', 1)
                return value.strip().strip('"').strip("'")
    return None 

def get_helper(line1):
    return line1[1]

def get_bug_type(line1): #nested locking bug reports have 6 words in line 1. Context confusion reports have 4
    if len(line1) == 6:  
        return 1 #nested locking bug
    return 0 #context confusion bug

def is_kfunc(helper):
    with open("kfuncs.json", "r") as kfunc_file:
        kfuncs_data = json.load(kfunc_file)
        if helper in kfuncs_data:
            return True
        return False

def is_map_helper(helper):
    if 'elem' in helper:
        return 1
    elif helper=="bpf_cgrp_storage_delete" or helper=="bpf_cgrp_storage_get" or helper=="bpf_get_stackid" or helper=="bpf_get_stack":
        return 1
    elif helper=="bpf_ringbuf_reserve" or helper=="bpf_ringbuf_output" or helper=="bpf_ringbuf_submit" or helper=="bpf_ringbuf_reserve_dynptr":
        return 1
    return 0

def is_timer_or_spinlock(helper):
    if 'bpf_timer' in helper:
        return 1
    if 'bpf_spin' in helper:
        return 1
    return 0

def get_map_type(helper):
    with open('specs.json', 'r') as specs_file:
        map_dicts = json.load(specs_file)
        for map_dict in map_dicts:
            for map_type in map_dict:
                if helper in map_dict[map_type]:
                    return map_type
        return ''

def transform_map_helper(helper):
    if 'update_elem' in helper:
        return 'bpf_map_update_elem'
    elif 'delete_elem' in helper:
        return 'bpf_map_delete_elem'
    elif 'lookup_elem' in helper:
        return 'bpf_map_lookup_elem'
    elif 'push_elem' in helper:
        return 'bpf_map_push_elem'
    elif 'pop_elem' in helper:
        return 'bpf_map_pop_elem'
    elif 'peek_elem' in helper:
        return 'bpf_map_peek_elem'
    else:
        #print("Unknown function")
        return helper

def get_possible_prog_types_kfunc(kfunc):
    with open ('kfuncs.json', 'r') as kfunc_file:
        kfunc_data = json.load(kfunc_file)
        if kfunc not in kfunc_data:
            print("kfunc not found")
        else:
            bpf_prog_types = kfunc_data[kfunc][2]
            possible_prog_types = []
            for bpf_prog_type in bpf_prog_types:
                possible_prog_types += convert_prog_type(bpf_prog_type)
            return possible_prog_types

def get_possible_prog_types_cc(helper):
    with open('../fptests/output/helper-progtype.json', 'r') as helper_progtype_file:
        helper_progtype = json.load(helper_progtype_file)

    if helper not in helper_progtype:
        possible_prog_types = []
        print("no prog types")
    else:
        possible_prog_types = helper_progtype[helper][0]
    return possible_prog_types

def get_prog_type_cc(helper):
    possible_prog_types=[]
    if is_kfunc(helper):
        possible_prog_types=get_possible_prog_types_kfunc(helper)
    else:
        possible_prog_types=get_possible_prog_types_cc(helper)
    with open('../utils/output/prog_type-context.json', 'r') as progtype_context_file:
        progtype_context = json.load(progtype_context_file)

    if not possible_prog_types:
        return ''

    #if we are working with a timer or spin lock function, the prog types cannot be tracing
    hierarchy = {'NMI':4, 'H':3, 'S':2, 'P':1}
    selected_type = ''
    max_context = 'P'
    for prog_type in possible_prog_types:
        if prog_type=='kprobe':
            selected_type=prog_type+'/my_nmi_handler'
            break
        if prog_type in progtype_context:
            context = progtype_context[prog_type][0]
            if hierarchy[context]>hierarchy[max_context]:
                max_context = context
                selected_type = prog_type
    return complete_attach(selected_type)

def get_lock_type(line):
    return line[-1]

def get_pre_function(line, orig_helper):
    if len(line)>=2:
        return line[-2][:-1]
    else:
        return orig_helper 

def get_possible_prog_types_nl(helper):
    with open('../fptests/output/precur.json', 'r') as precur_file:
        precur = json.load(precur_file)
        return precur[helper][0]

def get_prog_type_nl(helper, report_line, lock_type, orig_helper, pref):
    if is_kfunc(helper):
        possible_prog_types=get_possible_prog_types_kfunc(helper)
    else:
        possible_prog_types = get_possible_prog_types_nl(helper)
    
    if 'kprobe' in possible_prog_types and pref=="kprobe":
        prog_type = 'kprobe'  
    elif 'fentry' in possible_prog_types and pref=="fentry":
        prog_type = 'fentry'
    elif 'fentry' in possible_prog_types and pref=="fentry/unlock":
        prog_type = 'fentry'   
    elif 'tracepoint' in possible_prog_types and pref=="tracepoint":
        prog_type = 'tracepoint'
    else:
        print("skip test case")
        return ''
    attach_point = 'none'

    #check if map timer or spin lock needs to be used
    if is_timer_or_spinlock(helper):
        if 'fentry' not in possible_prog_types:
            print('false positive: no possible way to trigger bug since tracing programs cannot use timers or spinlocks')
            return ''
        else:
            prog_type = 'fentry'
    
    while attach_point == 'none' and report_line:
        pre_function = get_pre_function(report_line, orig_helper)
        attach_point = find_attach(pre_function, prog_type, lock_type, pref)
        report_line = report_line[:-1]
    if attach_point == 'none':
        return 'tracepoint/lock/lock_acquired'
    return prog_type+"/"+attach_point

def get_prog_type_secondary(helper):
    with open('../fptests/output/helper-progtype.json', 'r') as helper_progtype_file:
        helper_progtype = json.load(helper_progtype_file)

    if helper not in helper_progtype:
        possible_prog_types = []
        print("no prog types")
        return ''
    else:
        possible_prog_types = helper_progtype[helper][0]
    if "fentry" in possible_prog_types:
        return "fentry/do_nanosleep"
    else:
        return complete_attach(possible_prog_types[0])

def get_prog_type_secondary_kfunc(kfunc):
    possible_prog_types=get_possible_prog_types_kfunc(kfunc)
    if "fentry" in possible_prog_types:
        return "fentry/do_nanosleep"
    else:
        return complete_attach(possible_prog_types[0])

def get_params(helper):
    kernel_path=read_kernel_path()
    with open(kernel_path+'/include/uapi/linux/bpf.h', 'r') as helper_file:
        while True:
            line = helper_file.readline()
            if not line:
                break
            if helper+"(" in line:
                split_list = re.split('\(|\)|,',line)
                retfn_list = (split_list[0].split())
                
                return_type = retfn_list[1]
                if return_type=="struct":
                    return_type+=" "
                    return_type+=retfn_list[2]

                params = []
                for i in range(1, len(split_list)-1):
                    params.append(split_list[i])
                return(return_type, params)

def get_params_kfunc(helper):
    with open("kfuncs.json", "r") as kfunc_file:
        kfuncs_data = json.load(kfunc_file)
        if helper in kfuncs_data:
            return_type = kfuncs_data[helper][0]
            params = kfuncs_data[helper][1]
            return (return_type, params)

def get_info(report, pref):
    line1 = report[0]
    line2 = report[1]
    helper = get_helper(line1)
    orig_helper = helper
    map_type = ''
    bug_type = get_bug_type(line1)
    kfunc = False
    
    if is_kfunc(helper):
        kfunc = True
        prog_type2 = get_prog_type_secondary_kfunc(helper)
        params = get_params_kfunc(helper)    
    else:
        if is_map_helper(helper):
            map_type = get_map_type(helper)
            helper = transform_map_helper(helper)
        prog_type2 = get_prog_type_secondary(helper)
        params = get_params(helper)

    if bug_type == 0:
            prog_type1 = get_prog_type_cc(helper)
    else:
            lock_type = get_lock_type(line2)
            prog_type1 = get_prog_type_nl(helper, line2, lock_type, orig_helper, pref)
    
    print( helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper, kfunc)
    return ( helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper, kfunc)

'''
def get_report(report_file):
    result_file = open(report_file, "r")
    line1 = result_file.readline().split()
    line2 = result_file.readline().split()
    result_file.close()
    return (line1, line2)
'''

if __name__ == '__main__':
    helper = sys.argv[1]

    if is_kfunc(helper):
        print(get_params_kfunc(helper))
    else:
        if is_map_helper(helper):
            helper = transform_map_helper(helper)
        print(get_params(helper))

    '''
    report_file = "test_report.txt"
    report = get_report(report_file)

    get_info(report)
    '''

