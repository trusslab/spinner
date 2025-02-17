python3 poc.py
if [[ -f "output/poc_data.txt" ]]; then
    	output=$(cat output/poc_data.txt)
   	read -r helper prog_type1 prog_type2 <<< "$output"
else
    	echo "Error: output.txt not found!"
fi

python3 poc_loader.py $prog_type1 $prog_type2

if [[ "$prog_type1" == *"nmi"* ]]; then
	nmi=1
else
	nmi=0
fi

cd output
./build.sh poc

cd ..
./start_s2e.sh poc $helper $nmi

