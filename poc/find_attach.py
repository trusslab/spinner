import subprocess

# Define the command to run GDB and execute your script
def disassemble_function(function):
    gdb_command = [
        "gdb",
        "/home/priya/linux-6.9/vmlinux",
        "--batch",  # Run GDB in batch mode
        "-ex", f"disassemble {function}",  # Your command(s)
        "-ex", "quit"  # Quit GDB when done
    ]

    # Run the command and capture the output
    result = subprocess.run(gdb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode("utf-8")

    return output

def find_attach(function, program_type, lock_type):
    if program_type == 'tracepoint':
        return "lock/lock_acquired"
    
    elif program_type == 'kprobe':
        disassembled = disassemble_function(function)
        instrs = disassembled.split('\n')
        for i in range(len(instrs)):
            if lock_type in instrs[i]:
                offset_expression = instrs[i+1].split()[1]
                offset = offset_expression[offset_expression.index('<')+2:offset_expression.index('>')]
                return function+"+"+offset
        return 'none'

    elif program_type == 'fentry':
        disassembled = disassemble_function(function)
        instrs = disassembled.split('\n')
        lock_dict ={'_raw_spin_lock_irqsave': '_raw_spin_unlock_irqrestore', 
                '_raw_spin_lock_irq' : '_raw_spin_unlock_irq', 
                '_raw_spin_lock_bh': '_raw_spin_unlock_bh', 
                '_raw_spin_lock': '_raw_spin_unlock'}
        start_read = False
        for i in range(len(instrs)):
            if lock_type in instrs[i]:
                start_read = True
                continue
            if start_read and lock_dict[lock_type] in instrs[i]:
                return 'none'
            if start_read:
                instr_split = instrs[i].split()
                if instr_split[2] == 'call':
                    attach_function = instr_split[-1][1:-1]
                    return attach_function
        return 'none'
    else:
        return "not matching prog type"

if __name__=='__main__':
    print(find_attach('percpu_counter_add_batch', 'kprobe', '_raw_spin_lock'))
