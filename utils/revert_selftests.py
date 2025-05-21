import os
import re
import sys

directory = sys.argv[1]+'/tools/testing/selftests/bpf'

list = open('selftests_list.txt', 'w')

regex = re.compile('bpf\_printk\(\"hello unique string .*\"\)\;')

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.c'):
            f = open(os.path.join(root, file), 'r')
            lines = f.readlines()
            for i in range(len(lines)):
                if 'bpf_printk("hello unique string' in lines[i]:
                    lines[i] = regex.sub('', lines[i])
                
            f.close()
            list.write(file+"\n")
            list.writelines(lines) 
            
            f = open(os.path.join(root, file), 'w')
            f.writelines(lines)
            f.close()

