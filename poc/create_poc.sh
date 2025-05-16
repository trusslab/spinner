poc_name=$1
pref=$2

python3 poc.py $poc_name $pref
if [[ -f "output/poc_data.txt" ]]; then
    	output=$(cat output/poc_data.txt)
	if [[ $output == "fail" ]]; then
		exit
	fi
   	read -r helper prog_type1 prog_type2 bug_type <<< "$output"
else
    	echo "Error: output.txt not found!"
fi

python3 poc_loader.py $prog_type1 $prog_type2 $poc_name $helper

if [[ "$prog_type1" == *"nmi"* ]]; then
	nmi=1
else
	nmi=0
fi

cd output
./build.sh $poc_name

cd ..
./start_s2e.sh $poc_name $helper $nmi $bug_type

