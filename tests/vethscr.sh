ip netns add vpn 
ip link add name vethhost0 type veth peer name vethvpn0
ip link set vethvpn0 netns vpn
ip addr add 10.0.0.1/24 dev vethhost0
ip netns exec vpn ip addr add 10.0.0.2/24 dev vethvpn0
ip link set vethhost0 up
ip netns exec vpn ip link set vethvpn0 up

echo 1 > /proc/sys/net/ipv4/conf/all/forwarding
iptables -t nat -A PREROUTING ! -s 10.0.0.0/24 -p tcp -m tcp --dport 80 -j DNAT --to-destination 10.0.0.2
ip netns exec vpn ip route add default via 10.0.0.1

iptables -t nat -A POSTROUTING -d 10.0.0.2/24 -j SNAT --to-source 10.0.0.1

iptables -t nat -A OUTPUT -d 192.168.1.2 -p tcp -m tcp --dport 80 -j DNAT --to-destination 10.0.0.2

ip netns exec vpn ip link set dev vethvpn0 up
ip netns exec vpn nc -l -s 10.0.0.2 -p 80 &

