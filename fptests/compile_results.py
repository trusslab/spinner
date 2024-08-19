import re
import pandas
from pandas import DataFrame

helper_progtype_file = open("output/helper-progtype.txt", "r")
helper_functions = []
allowed_prog_types = []
disallowed_prog_types = []
needs_check = []
dict_helpers = {}


while True:
    line = helper_progtype_file.readline()
    if not line:
        break
    arr = line.split()
    if len(arr) == 5:
        if arr[0] not in helper_functions:
            empty1 = []
            empty2 = []
            empty3 = []
            dict_helpers[arr[0]] = [empty1, empty2, empty3]

#print(dict_helpers)

helper_progtype_file.seek(0)
while True:
    line = helper_progtype_file.readline()
    if not line:
        break
    arr = line.split()
    if len(arr) == 5:
        if arr[4] == "yes":
            dict_helpers[arr[0]][0].append(arr[1])
        else:
            dict_helpers[arr[0]][1].append(arr[1])
        if arr[2] =="yes" or arr[3]=="yes":
            dict_helpers[arr[0]][2].append("check "+arr[0]+" with "+arr[1])



tracing_prog_types = ['perf_event', 'tracepoint', 'tp', 'raw_tp.w', 'raw_tracepoint.w', 'raw_tp', 'raw_tracepoint', 'kprobe', 'kretprobe', 'kprobe.multi', 
        'kretprobe.multi', 'uprobe', 'uprobe.s', 'uretprobe', 'uretprobe.s', 'usdt', 'fmod_ret', 'fmod_ret.s', 'fentry', 'fentry.s', 'fexit', 'fexit.s',
        'iter', 'iter.s', 'tp_btf']
potential_recur_funcs = []
precur_file = open("output/precur.txt", "w")
for key in dict_helpers:
    helper_functions.append(key)
    allowed_prog_types.append(dict_helpers[key][0])
    disallowed_prog_types.append(dict_helpers[key][1])
    needs_check.append(dict_helpers[key][2])


    tp = False
    non_tp = False
    tp_prog_type = []
    non_tp_prog_type = []
    for prog_type in dict_helpers[key][0]:
        if prog_type in tracing_prog_types:
            tp = True
            tp_prog_type.append(prog_type)
        if prog_type not in tracing_prog_types:
            non_tp = True
            non_tp_prog_type.append(prog_type)
    if tp and non_tp:
        result = key+" can be called by "+str(tp_prog_type)+" and "+str(non_tp_prog_type)+"\n"
        potential_recur_funcs.append(result)
precur_file.writelines(potential_recur_funcs)
precur_file.close()

df = DataFrame({"Helper function":helper_functions, "Allowed program types" : allowed_prog_types, "Disallowed program types": disallowed_prog_types, "Needs check": needs_check})

print(df)
print(len(helper_functions))

df.to_excel('helper-progtype-results.xlsx', sheet_name = 'sheet1', index = False)
helper_progtype_file.close()

