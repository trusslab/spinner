source config.conf
poc_dir=$(pwd)

poc_binary=$1
poc_helper=$2
nmi=$3
bug_type=$4

s2e_env_dir=$S2E_ENV_DIR 
s2e_dir=$S2E_DIR

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
\${S2ECMD} put syslog.txt

sudo cp /proc/lockdep lockdep.txt
sudo chmod 777 lockdep.txt
\${S2ECMD} put lockdep.txt

sudo cp /proc/lockdep_chains lockdep_chains.txt
sudo chmod 777 lockdep_chains.txt
\${S2ECMD} put lockdep_chains.txt

sudo cp /proc/lockdep_stats lockdep_stats.txt
sudo chmod 777 lockdep_stats.txt
\${S2ECMD} put lockdep_stats.txt

sudo cp /proc/lock_stat lock_stat.txt
sudo chmod 777 lock_stat.txt
\${S2ECMD} put lock_stat.txt

sudo cp /proc/locks locks.txt
sudo chmod 777 locks.txt
\${S2ECMD} put locks.txt

sudo ./$poc_binary > output.txt 2>&1
\${S2ECMD} put output.txt
EOF

nm_result=$(nm -n guestfs/vmlinux | grep " $poc_helper$")
function_address="${nm_result%% *}"

nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_lock_irqsave$")
irqsaveLockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_unlock_irqrestore$")
irqrestoreUnlockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_lock_irq$")
irqLockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_unlock_irq$")
irqUnlockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_lock_bh$")
bhLockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_unlock_bh$")
bhUnlockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_lock$")
lockAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep " _raw_spin_unlock$")
unlockAddress="${nm_result%% *}"

nm_result=$(nm -n guestfs/vmlinux | grep "print_usage_bug")
printUsageBugAddress="${nm_result%% *}"
nm_result=$(nm -n guestfs/vmlinux | grep "print_lock_invalid_wait_context")
#printInvalidWaitBugAddress="${nm_result%% *}"
printInvalidWaitBugAddress="ffffffff811200d3"


s2e_config_file="s2e-config.lua"
sed -i "/generateOnStateKill/d" "$s2e_config_file"
sed -i "/generateOnSegfault/d" "$s2e_config_file"
if [[ $bug_type == 1 ]]; then
	cat <<EOF >> "$s2e_config_file"

add_plugin("DeadlockTimer")
pluginsConfig.DeadlockTimer = {
        startAddress = 0x$function_address,
        irqsaveLockAddress = 0x$irqsaveLockAddress,
        irqrestoreUnlockAddress = 0x$irqrestoreUnlockAddress,
        irqLockAddress = 0x$irqLockAddress,
        irqUnlockAddress = 0x$irqUnlockAddress,
        bhLockAddress = 0x$bhLockAddress,
        bhUnlockAddress = 0x$bhUnlockAddress,
        lockAddress = 0x$lockAddress,
        unlockAddress = 0x$unlockAddress,
}

add_plugin("ForkEBPF")
add_plugin("ExceptionTracer")
EOF

else 
	cat <<EOF >> "$s2e_config_file"
add_plugin("LockdepCheck")
pluginsConfig.LockdepCheck = {
	lockdepUsageBugAddress = 0x$printUsageBugAddress,
	lockdepInvalidWaitAddress = 0x$printInvalidWaitBugAddress,
} 

add_plugin("ForkEBPF")
add_plugin("ExceptionTracer")
EOF
fi

s2e_launch_file="launch-s2e.sh"
sed -i 's/^export S2E_MAX_PROCESSES=[0-9]*$/export S2E_MAX_PROCESSES=48/' "$s2e_launch_file"
sed -i 's|trap "kill \$CHILD_PID" SIGINT|trap "kill -TERM -\$CHILD_PID" SIGINT SIGTERM SIGHUP|' "$s2e_launch_file"

cd $poc_dir
./compile_probe.sh $poc_binary $poc_helper

#./launch-s2e.sh

