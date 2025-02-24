step6=`date +%s`
cd graphtraverse
bash -c "python3 graphtraverse.py>file_complete"
step7=`date +%s`

echo $step6
echo $step7
