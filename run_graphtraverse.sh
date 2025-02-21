step6=`date +%s`
cd graphtraverse
bash -c "python3 graphtraverse.py>file"
step7=`date +%s`

echo $step6
echo $step7
