import os

folder = '/sys/kernel/tracing/events'
tracepoint_file = open("tracepoints.txt", "w")


sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

for sub_folder in sub_folders:
    path = folder+"/"+sub_folder
    events = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    print(events)

    for event in events:
        tracepoint_file.write("trace_"+event+"\n")

tracepoint_file.close()
#print(sub_folders)

results_file = open("libppf-bootstrap/examples/c/helper-progtype-copy.txt", "r")
tp_helpers = []
tp_progtypes = ['raw_tp.w', 'raw_tracepoint.w', 'raw_tp', 'raw_tracepoint', 'tp', 'tracepoint']
while(True):
    line = results_file.readline()
    if not line:
        break
    results = line.split()
    if results[1] in tp_progtypes and results[4]=='yes':
        if results[0] not in tp_helpers:
            tp_helpers.append(results[0])

tp_helpers_file = open("tp_helpers.txt", "w")
for line in lines:
    f.write(f"{line}\n")
tp_helpers_file.close()

