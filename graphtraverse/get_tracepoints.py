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
