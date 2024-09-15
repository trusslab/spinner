import os
import re

directory = '/home/priya/linux-6.9/tools/testing/selftests/bpf'

list = open('selftests_list.txt', 'w')

read_start = False
attach_to = ''

skip_list = ['test_static_linked1.c', 'test_static_linked2.c', 'linked_funcs1.c', 'linked_funcs2.c', 'linked_vars1.c', 'linked_vars2.c', 
        'linked_maps1.c', 'linked_maps2.c', 'test_subskeleton_lib.c', 'test_subskeleton_lib2.c']

for root, dirs, files in os.walk(directory):
    for file in files:
        print(file)
        if file.endswith('.c'):
            f = open(os.path.join(root, file), 'r')
            mod = False
            skip = False
            License = False
            lines = f.readlines()

            for i in range(len(lines)):
             
                if "SEC(\"license\")" in lines[i]:
                    License = True
                    lines[i] = "char License[] SEC(\"license\") = \"Dual BSD/GPL\";\n"
                
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
                        if file == "rbtree_fail.c":
                            insert_line = ''
                        elif file == 'struct_ops_multi_pages.c' and "struct_ops/tramp" in attach_to:
                            insert_line = 'bpf_printk("hello unique string struct_ops/tramp");'
                        elif "struct_ops/test_1" not in attach_to and 'lsm/bpf' not in attach_to:
                            insert_line = 'bpf_printk("hello unique string '+attach_to+'");'
                        lines[i] = lines[i][:index+1]+insert_line+lines[i][index+1:]
                    else:
                        skip=False
            if License == False and file not in skip_list:
                lines.append("char License[] SEC(\"license\") = \"Dual BSD/GPL\";\n")
            f.close()
            list.write(file+"\n")
            list.writelines(lines) 
            
            
            if mod==True:
                f = open(os.path.join(root, file), 'w')
                f.writelines(lines)
                f.close()
           
