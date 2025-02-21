import json
import re
import sys
from find_attach import find_attach


def get_helper(line1):
    return line1[1]

def get_bug_type(line1): #nested locking bug reports have 6 words in line 1. Context confusion reports have 4
    if len(line1) == 6:  
        return 1 #nested locking bug
    return 0 #context confusion bug

def is_map_helper(helper):
    if 'elem' in helper:
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
    else:
        print("Unknown function")
        return helper

def get_prog_type_cc(helper):
    with open('/home/priya/defogger/fptests/output/helper-progtype.json', 'r') as helper_progtype_file:
        helper_progtype = json.load(helper_progtype_file)

    with open('/home/priya/copy/prog_type-context.json', 'r') as progtype_context_file:
        progtype_context = json.load(progtype_context_file)

    if helper not in helper_progtype:
        possible_prog_types = []
        print("no prog types")
        return ''
    else:
        possible_prog_types = helper_progtype[helper][0]

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
    return selected_type

def get_lock_type(line):
    return line[-1]

def get_pre_function(line):
    if len(line)>=2:
        return line[-2][:-1]

def get_prog_type_nl(helper, report_line, lock_type):
    with open('/home/priya/defogger/fptests/output/precur.json', 'r') as precur_file:
        precur = json.load(precur_file)
    if 'kprobe' in precur[helper][0]:
        prog_type = 'kprobe'
    elif 'tracepoint' in precur[helper][0]:
        prog_type = 'tracepoint'
    elif 'fentry' in precur[helper][0]:
        prog_type = 'fentry'
    else:
        print('edge case: need to reexamine')
        return precur[helper][0][0]
    attach_point = 'none'
    while attach_point == 'none' and report_line:
        pre_function = get_pre_function(report_line)
        attach_point = find_attach(pre_function, prog_type, lock_type)
        report_line = report_line[:-1]
    return prog_type+"/"+attach_point

def get_prog_type_secondary(helper):
    with open('/home/priya/defogger/fptests/output/helper-progtype.json', 'r') as helper_progtype_file:
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
        return possible_prog_types[0]

def get_params(helper):
    with open('/home/priya/defogger/fptests/bpf.h', 'r') as helper_file:
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

def get_info(report):
    line1 = report[0]
    line2 = report[1]
    helper = get_helper(line1)
    orig_helper = helper
    map_type = ''
    bug_type = get_bug_type(line1)
    if is_map_helper(helper):
        map_type = get_map_type(helper)
        helper = transform_map_helper(helper)
    if bug_type == 0:
        prog_type1 = get_prog_type_cc(helper)
    else:
        lock_type = get_lock_type(line2)
        prog_type1 = get_prog_type_nl(helper, line2, lock_type)
    prog_type2 = get_prog_type_secondary(helper)
    params = get_params(helper)
    print( helper, bug_type, map_type, prog_type1, prog_type2, params)
    return ( helper, bug_type, map_type, prog_type1, prog_type2, params, orig_helper)

if __name__ == '__main__':
    helper = sys.argv[1]
    if is_map_helper(helper):
        helper = transform_map_helper(helper)
    print(get_params(helper))
