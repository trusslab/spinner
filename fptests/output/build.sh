clang -O2 -target bpf -g -D__TARGET_ARCH_x86 -I/usr/include/bpf/\
	-I/usr/local/include/bpf/\
	-c output/test.bpf.c -o output/test.bpf.o \
	#-I../../libbpf/include/uapi -I/usr/local/include -I/usr/include/x86_64-linux-gnu \
	#-I/usr/lib/llvm-17/lib/clang/17/include \
	#-I/usr/lib64/ -I../../libbpf/src \
gcc -g -L/usr/lib64/ -o output/test output/test.c  -lbpf  

#-I../../libbpf/src -L/usr/lib64/ 

