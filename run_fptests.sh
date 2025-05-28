KDIR=$1
sudo cp -r /usr/include/asm-generic /usr/include/asm

cd fptests/output
bpftool btf dump file /sys/kernel/btf/vmlinux format c> vmlinux.h
cd ..

bpftool btf dump file /sys/kernel/btf/vmlinux format c> "$KDIR/tools/testing/selftests/bpf/progs/vmlinux.h"

bash -c "sudo python3 run_test.py $KDIR"

