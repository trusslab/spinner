import re

helper_file = open("bpf.h", "r")
read_start = False
count=0
while True:
    line = helper_file.readline()
    if not line:
        break
    if " * Start of BPF helper function descriptions:" in line:
        read_start=True
    if "*/" in line and read_start==True:
        read_start=False
    if read_start==True and re.search("^ [*] ([a-z]|[A-Z]|[_])", line): 
        count+=1

print(count)
