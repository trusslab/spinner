import os
import re

directory = '/home/priya/linux-6.9/tools/testing/selftests/bpf'

list = open('selftests_list.txt', 'w')

read_start = False
attach_to = ''

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.c'):
            f = open(os.path.join(root, file), 'r')
            mod = False
            skip = False
            lines = f.readlines()
            for i in range(len(lines)):
                
                
                if re.match('^SEC\(\"([a-zA-Z]|\/|\?|_)', lines[i].strip()):
                    read_start = True
                    index_start = lines[i].index("(")
                    index_end = lines[i].index(")")
                    attach_to = lines[i][index_start+2:index_end-1]
                
                if read_start == True and "__naked" in lines[i]:
                    skip=True

                if read_start == True and "." in attach_to:
                    skip= True
                
                if read_start == True and "{" in lines[i]:
                    read_start = False
                    if skip==False:
                        mod=True
                        index = lines[i].index("{")
                        #if macro==True:
                            #insert_line = 'bpf_printk("hello unique string"); \\'
                        #print(attach_to) 
                        insert_line = 'bpf_printk("hello unique string '+attach_to+'");'
                        lines[i] = lines[i][:index+1]+insert_line+lines[i][index+1:]
                    else:
                        skip=False
            f.close()
            list.write(file+"\n")
            list.writelines(lines) 
            
            
            if mod==True:
                f = open(os.path.join(root, file), 'w')
                f.writelines(lines)
                f.close()
           
