clang -O2 -target bpf -g -D__TARGET_ARCH_x86 -I/home/priya/libbpf/include/uapi -I/usr/local/include -I/usr/include/x86_64-linux-gnu \
	-I/usr/include -I/usr/lib/llvm-17/lib/clang/17/include -c output/test.bpf.c -o output/test.bpf.o 
gcc -o output/test output/test.c -lbpf

