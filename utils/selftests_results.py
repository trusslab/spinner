import pandas
from pandas import DataFrame
import json

f = open("/sys/kernel/debug/tracing/trace", "r")

context_dict = {}
irqs_dict = {}
max_context_dict = {}
max_irqs_dict = {}
num_tests_dict = {}

lines = f.readlines()
for line in lines:
    if not line:
        continue
    split_line = line.split()
    if len(split_line)<9:
        continue
    info = split_line[2]
    attach_type = split_line[-1]
    prog_type = attach_type.split('/')[0]
    second_type = ''
    if len(attach_type.split('/')) >=2:
        second_type = attach_type.split('/')[1]
    prog_type = prog_type.replace('?', '')
    prog_type = ''.join([i for i in prog_type if not i.isdigit()])
    with_second_type = ['cgroup', 'cgroup_skb', 'sk_reuseport', 'sk_skb', 'xdp', 'xdp.frags']
    if prog_type in with_second_type and second_type!='':
        prog_type+='/'
        prog_type+=second_type

    if info[0] == '[':
        continue

    context = ''
    if info[2]=='.':
        context = 'P'
    elif info[2] == 's' :
        context = 'S'
    elif info[2] == 'H' or info[2] == 'h':
        context = 'H'
    elif info[2] =='Z' or info[2] =='z':
        context = 'NMI'
    else:
        context = info

    irqs = ''
    if info[0] == '.':
        irqs ='.'
    elif info[0] == 'b':
        irqs = 'b'
    elif info[0] == 'd' or info[0] == 'D':
        irqs = 'd'
    else:
        irqs = info

    if prog_type not in context_dict:
        context_dict[prog_type] = []
        num_tests_dict[prog_type] = 0
        irqs_dict[prog_type] = []

    num_tests_dict[prog_type] += 1
    if context not in context_dict[prog_type]:
        context_dict[prog_type].append(context)
    if irqs not in irqs_dict[prog_type]:
        irqs_dict[prog_type].append(irqs)

#print(context_dict)

hierarchy = {'NMI': 0, 'H': 1, 'S':2, 'P':3}
for prog_type in context_dict:
    for context in context_dict[prog_type]:
        if prog_type not in max_context_dict:
            max_context_dict[prog_type] = context
        else:
            if hierarchy[context]<hierarchy[max_context_dict[prog_type]]:
                max_context_dict[prog_type] = context

hierarchy = {'d': 0, 'b': 1, '.':2}
for prog_type in irqs_dict:
    for irqs in irqs_dict[prog_type]:
        if prog_type not in max_irqs_dict:
            max_irqs_dict[prog_type] = irqs
        else:
            if hierarchy[irqs]<hierarchy[max_irqs_dict[prog_type]]:
                max_irqs_dict[prog_type] = irqs



prog_types = []
max_contexts = []
num_tests = []
irqs_list = []
json_dict = {}
for prog_type in max_context_dict:
    prog_types.append(prog_type)
    max_contexts.append(max_context_dict[prog_type])
    num_tests.append(num_tests_dict[prog_type])
    irqs_list.append(irqs_dict[prog_type])
    json_dict[prog_type] = [max_context_dict[prog_type], max_irqs_dict[prog_type]]
    print(prog_type+" : "+max_context_dict[prog_type]+" : "+str(num_tests_dict[prog_type]))

df = DataFrame({"Program Type":prog_types, "Max Context" :max_contexts, "IRQS" :irqs_list, "Number of tests": num_tests})
print(df.head)
df.to_excel('output/prog_type-context.xlsx', sheet_name = 'sheet1', index = False)

json_object = json.dumps(json_dict)

with open('output/prog_type-context.json', "w") as outfile:
    outfile.write(json_object)
