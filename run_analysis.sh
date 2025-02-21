step1=`date +%s`
cd utils
bash -c "python3 mod_selftests.py"
step2=`date +%s`
bash -c "make -C $1/tools/testing/selftests/bpf run_tests -j$(nproc)"
step3=`date +%s`
bash -c "python3 revert_selftests.py"
bash -c "python3 selftests_results.py"
step4=`date +%s`
cd ../mlta
touch callgraph.dot
make
bash -c "./build/lib/kanalyzer @bc.list"
step5=`date +%s`
cd ../fptests/output
bpftool btf dump file /sys/kernel/btf/vmlinux format c> vmlinux.h
cd ..
bash -c "python3 run_test.py"
step6=`date +%s`
cd ../graphtraverse
bash -c "python3 graphtraverse.py>results.txt"
step7=`date +%s`

echo "$step1\n"
echo "$step2\n"
echo "$step3\n"
echo "$step4\n"
echo "$step5\n"
echo "$step6\n"
echo "$step7\n"

