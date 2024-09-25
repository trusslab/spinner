cd utils
bash -c "python3 mod_selftests.py"
bash -c "make -C $1/tools/testing/selftests/bpf run_tests -j16"
bash -c "python3 revert_selftests.py"
bash -c "python3 selftests_results.py"
cd ../mlta
bash -c "./build/lib/kanalyzer @bc.list"
cd ../fptests/output
bpftool btf dump file /sys/kernel/btf/vmlinux format c> vmlinux.h
cd ..
bash -c "python3 run_test.py"
cd ../graphtraverse
bash -c "python3 graphtraverse.py>results.txt"
