cd mlta
touch callgraph.dot
make
./build/lib/kanalyzer @bc.list
cd ..
