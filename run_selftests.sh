KDIR=$1
CUR_DIR=$(pwd)

cd utils
sudo python3 mod_selftests.py $KDIR

cd $KDIR
bash -c "sudo make -C tools/testing/selftests/bpf -j8"
bash -c "sudo make -C tools/testing/selftests/bpf run_tests"
cd $CUR_DIR/utils

sudo python3 revert_selftests.py $KDIR
mkdir output
sudo python3 selftests_results.py

