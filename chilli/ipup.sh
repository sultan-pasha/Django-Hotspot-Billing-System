#UAM server specified as 10.0.0.1
iptables -I INPUT -i tun0 -p tcp -m tcp --dport 80 --dst 10.0.0.1 -j ACCEPT
iptables -I INPUT -i tun0 -p tcp -m tcp --dport 443 --dst 10.0.0.1 -j ACCEPT
iptables -I INPUT -i tun0 -p tcp -m tcp --dport 22 --dst 10.0.0.1 -j ACCEPT
iptables -I INPUT -i tun0 -p tcp -m tcp --dport 8000 --dst 10.0.0.1 -j ACCEPT
# force-add the final rule necessary to fix routing tables (Enabling NAT)
iptables -F POSTROUTING -t nat
iptables -I POSTROUTING -t nat -o $HS_WANIF -j MASQUERADE
