poc_dir=$(pwd)

poc_binary=$1
poc_helper=$2
nmi=$3
bug_type=$4

s2e_env_dir=/home/priya/s2e-env 

s2e_dir=/home/priya/s2e

cd $s2e_env_dir
. venv/bin/activate
source $s2e_dir/s2e_activate

cd $poc_dir/output

s2e new_project --image debian-12.5-x86_64 $poc_binary
cp $poc_binary.bpf.o $s2e_dir/projects/$poc_binary

cd $s2e_dir/projects/$poc_binary

bootstrap_file="bootstrap.sh"

sed -i "/\${S2ECMD} get \"$poc_binary\"/a \\
\${S2ECMD} get \"$poc_binary.bpf.o\"" "$bootstrap_file"

sed -i '/S2E_SO="${TARGET_TOOLS64_ROOT}\/s2e.so"/a \
    sudo chown root ${TARGET}\
    sudo chmod u+s ${TARGET}' "$bootstrap_file"

sed -i '/prepare_target "${TARGET_PATH}"/a \
	${S2ECMD} get probe.ko\
	sudo staprun probe.ko -L' "$bootstrap_file"

if [[ $nmi==1 ]]; then
	sed -i '/prepare_target "${TARGET_PATH}"/a \
		${S2ECMD} get nmi_example.ko \
		sudo insmod nmi_example.ko' "$bootstrap_file"
fi

cat <<EOF >> "$bootstrap_file"

sudo cp /sys/kernel/debug/tracing/trace trace.txt
sudo chmod 777 trace.txt
\${S2ECMD} put trace.txt

sudo dmesg > dmesg.txt
\${S2ECMD} put dmesg.txt

uname -r > uname.txt
\${S2ECMD} put uname.txt

sudo cp /var/log/syslog syslog.txt
sudo chmod 777 syslog.txt
${S2ECMD} put syslog.txt

sudo cp /proc/lockdep lockdep.txt
sudo chmod 777 lockdep.txt
${S2ECMD} put lockdep.txt

sudo cp /proc/lockdep_chains lockdep_chains.txt
sudo chmod 777 lockdep_chains.txt
${S2ECMD} put lockdep_chains.txt

sudo cp /proc/lockdep_stats lockdep_stats.txt
sudo chmod 777 lockdep_stats.txt
${S2ECMD} put lockdep_stats.txt

sudo cp /proc/lock_stat lock_stat.txt
sudo chmod 777 lock_stat.txt
${S2ECMD} put lock_stat.txt

sudo cp /proc/locks locks.txt
sudo chmod 777 locks.txt
${S2ECMD} put locks.txt
EOF


s2e_config_file="s2e-config.lua"
sed -i "/generateOnStateKill/d" "$s2e_config_file"
sed -i "/generateOnSegfault/d" "$s2e_config_file"
if [[ $bug_type == 1 ]]; then
	cat <<EOF >> "$s2e_config_file"

add_plugin("DeadlockTimer")
pluginsConfig.DeadlockTimer = {
        startAddress = 0xffffffff81267524,
        irqsaveLockAddress = 0xffffffff81a3ecb4,
        irqrestoreUnlockAddress = 0xffffffff81a3efc4,
        irqLockAddress = 0xffffffff81a3ec14,
        irqUnlockAddress = 0xffffffff81a3ef74 ,
        bhLockAddress = 0xffffffff81a3eb94,
        bhUnlockAddress = 0xffffffff81a3ef34,
        lockAddress = 0xffffffff81a3ea24,
        unlockAddress = 0xffffffff81a3eee4,
}

EOF

else 
	cat <<EOF >> "$s2e_config_file"
add_plugin("LockdepCheck")
pluginsConfig.LockdepCheck = {
	lockdepPrintAddress = 0xffffffff8111e120,
} 
EOF
fi

cd $poc_dir
./compile_probe.sh $poc_binary $poc_helper

#./launch-s2e.sh

