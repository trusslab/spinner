prog=$1

clang -O2 -target bpf -g -D__TARGET_ARCH_x86 -c $prog.bpf.c -o $prog.bpf.o 
gcc -L/usr/lib64 -o $prog $prog.c -lbpf -g

