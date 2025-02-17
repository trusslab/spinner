poc_dir=$(pwd)

poc_binary=$1
poc_helper=$2
nmi=$3

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

sudo trace-cmd show > trace-cmd.txt
\${S2ECMD} put trace-cmd.txt
EOF


cd $poc_dir
./compile_probe.sh $poc_binary $poc_helper

#./launch-s2e.sh

