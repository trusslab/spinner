KDIR=$1

cd "$KDIR/tools/lib/bpf"
make
sudo make install

cd "$KDIR/tools/bpf/bpftool"
make 
sudo make install

echo "/usr/local/lib64" | sudo tee /etc/ld.so.conf.d/libbpf.conf
sudo ldconfig
