KDIR=$1

cd fptests/output
bpftool btf dump file /sys/kernel/btf/vmlinux format c> vmlinux.h
cd ..

bpftool btf dump file /sys/kernel/btf/vmlinux format c> "$KDIR/tools/testing/selftests/bpf/progs/vmlinux.h"

bash -c "sudo python3 run_test.py $KDIR"

