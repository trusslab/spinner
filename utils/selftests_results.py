import pandas
from pandas import DataFrame

f = open("/sys/kernel/debug/tracing/trace", "r")

context_dict = {}
irqs_dict = {}
max_context_dict = {}
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
    prog_type = prog_type.replace('?', '')
    prog_type = ''.join([i for i in prog_type if not i.isdigit()])

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
    elif info[0] == 'd':
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
            if hierarchy[context]>hierarchy[max_context_dict[prog_type]]:
                max_context_dict[prog_type] = context

prog_types = []
max_contexts = []
num_tests = []
irqs_list = []
for prog_type in max_context_dict:
    prog_types.append(prog_type)
    max_contexts.append(max_context_dict[prog_type])
    num_tests.append(num_tests_dict[prog_type])
    irqs_list.append(irqs_dict[prog_type])
    print(prog_type+" : "+max_context_dict[prog_type]+" : "+str(num_tests_dict[prog_type]))

df = DataFrame({"Program Type":prog_types, "Max Context" :max_contexts, "IRQS" :irqs_list, "Number of tests": num_tests})
print(df.head)
df.to_excel('prog_type-context.xlsx', sheet_name = 'sheet1', index = False)
