#!/bin/bash

if readlink /proc/$$/exe | grep -q "dash"; then
        echo 'This installer needs to be run with "bash", not "sh".'
        exit
fi

# Discard stdin. Needed when running from an one-liner which includes a newline
read -N 999999 -t 0.001

# Detect OpenVZ 6
if [[ $(uname -r | cut -d "." -f 1) -eq 2 ]]; then
        echo "The system is running an old kernel, which is incompatible with this installer."
        exit
fi

MYDIR=$(dirname $0)

# Detect OS
# $os_version variables aren't always in use, but are kept here for convenience
if grep -qs "ubuntu" /etc/os-release; then
        os="ubuntu"
        os_version=$(grep 'VERSION_ID' /etc/os-release | cut -d '"' -f 2 | tr -d '.')
        group_name="nogroup"
elif [[ -e /etc/debian_version ]]; then
        os="debian"
        os_version=$(grep -oE '[0-9]+' /etc/debian_version | head -1)
        group_name="nogroup"
elif [[ -e /etc/centos-release ]]; then
        os="centos"
        os_version=$(grep -oE '[0-9]+' /etc/centos-release | head -1)
        group_name="nobody"
elif [[ -e /etc/fedora-release ]]; then
        os="fedora"
        os_version=$(grep -oE '[0-9]+' /etc/fedora-release | head -1)
        group_name="nobody"
else
        echo "This installer seems to be running on an unsupported distribution.
Supported distributions are Ubuntu, Debian, CentOS, and Fedora."
        exit
fi

if [[ "$os" == "ubuntu" && "$os_version" -lt 1804 ]]; then
        echo "Ubuntu 18.04 or higher is required to use this installer.
This version of Ubuntu is too old and unsupported."
        exit
fi

if [[ "$os" == "debian" && "$os_version" -lt 9 ]]; then
        echo "Debian 9 or higher is required to use this installer.
This version of Debian is too old and unsupported."
        exit
fi

if [[ "$os" == "centos" && "$os_version" -lt 7 ]]; then
        echo "CentOS 7 or higher is required to use this installer.
This version of CentOS is too old and unsupported."
        exit
fi

# Detect environments where $PATH does not include the sbin directories
if ! grep -q sbin <<< "$PATH"; then
        echo '$PATH does not include sbin. Try using "su -" instead of "su".'
        exit
fi

if [[ "$EUID" -ne 0 ]]; then
        echo "This installer needs to be run with superuser privileges."
        exit
fi

if [[ ! -e /dev/net/tun ]] || ! ( exec 7<>/dev/net/tun ) 2>/dev/null; then
        echo "The system does not have the TUN device available.
TUN needs to be enabled before running this installer."
        exit
fi



if [[ ! -e /etc/openvpn/server/server.conf ]]; then
        clear
        echo 'Welcome to this OpenVPN road warrior installer!'
        # If system has a single IPv4, it is selected automatically. Else, ask the user
        if [[ $(ip -4 addr | grep inet | grep -vEc '127(\.[0-9]{1,3}){3}') -eq 1 ]]; then
                ip=$(ip -4 addr | grep inet | grep -vE '127(\.[0-9]{1,3}){3}' | cut -d '/' -f 1 | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}')
        else
                number_of_ip=$(ip -4 addr | grep inet | grep -vEc '127(\.[0-9]{1,3}){3}')
                echo
                echo "Which IPv4 address should be used?"
                ip -4 addr | grep inet | grep -vE '127(\.[0-9]{1,3}){3}' | cut -d '/' -f 1 | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}' | nl -s ') '
                read -p "IPv4 address [1]: " ip_number
                until [[ -z "$ip_number" || "$ip_number" =~ ^[0-9]+$ && "$ip_number" -le "$number_of_ip" ]]; do
                        echo "$ip_number: invalid selection."
                        read -p "IPv4 address [1]: " ip_number
                done
                [[ -z "$ip_number" ]] && ip_number="1"
                ip=$(ip -4 addr | grep inet | grep -vE '127(\.[0-9]{1,3}){3}' | cut -d '/' -f 1 | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}' | sed -n "$ip_number"p)
        fi
        # If $ip is a private IP address, the server must be behind NAT
        if echo "$ip" | grep -qE '^(10\.|172\.1[6789]\.|172\.2[0-9]\.|172\.3[01]\.|192\.168)'; then
                echo
                echo "This server is behind NAT. What is the public IPv4 address or hostname?"
                # Get public IP and sanitize with grep
                get_public_ip=$(grep -m 1 -oE '^[0-9]{1,3}(\.[0-9]{1,3}){3}$' <<< "$(wget -T 10 -t 1 -4qO- "http://ip1.dynupdate.no-ip.com/" || curl -m 10 -4Ls "http://ip1.dynupdate.no-ip.com/")")
                read -p "Public IPv4 address / hostname [$get_public_ip]: " public_ip
                # If the checkip service is unavailable and user didn't provide input, ask again
                until [[ -n "$get_public_ip" || -n "$public_ip" ]]; do
                        echo "Invalid input."
                        read -p "Public IPv4 address / hostname: " public_ip
                done
                [[ -z "$public_ip" ]] && public_ip="$get_public_ip"
        fi
        # If system has a single IPv6, it is selected automatically
        if [[ $(ip -6 addr | grep -c 'inet6 [23]') -eq 1 ]]; then
                ip6=$(ip -6 addr | grep 'inet6 [23]' | cut -d '/' -f 1 | grep -oE '([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}')
        fi
        # If system has multiple IPv6, ask the user to select one
        if [[ $(ip -6 addr | grep -c 'inet6 [23]') -gt 1 ]]; then
                number_of_ip6=$(ip -6 addr | grep -c 'inet6 [23]')
                echo
                echo "Which IPv6 address should be used?"
                ip -6 addr | grep 'inet6 [23]' | cut -d '/' -f 1 | grep -oE '([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}' | nl -s ') '
                read -p "IPv6 address [1]: " ip6_number
                until [[ -z "$ip6_number" || "$ip6_number" =~ ^[0-9]+$ && "$ip6_number" -le "$number_of_ip6" ]]; do
                        echo "$ip6_number: invalid selection."
                        read -p "IPv6 address [1]: " ip6_number
                done
                [[ -z "$ip6_number" ]] && ip6_number="1"
                ip6=$(ip -6 addr | grep 'inet6 [23]' | cut -d '/' -f 1 | grep -oE '([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}' | sed -n "$ip6_number"p)
        fi
        echo
        echo "Which protocol should OpenVPN use?"
        echo "   1) UDP (recommended)"
        echo "   2) TCP"
        read -p "Protocol [1]: " protocol
        until [[ -z "$protocol" || "$protocol" =~ ^[12]$ ]]; do
                echo "$protocol: invalid selection."
                read -p "Protocol [1]: " protocol
        done
        case "$protocol" in
                1|"")
                protocol=udp
                ;;
                2)
                protocol=tcp
                ;;
        esac
        echo
        echo "What port should OpenVPN listen to?"
        read -p "Port [1194]: " port
        until [[ -z "$port" || "$port" =~ ^[0-9]+$ && "$port" -le 65535 ]]; do
                echo "$port: invalid port."
                read -p "Port [1194]: " port
        done
        [[ -z "$port" ]] && port="1194"
        
        
        echo
        echo "OpenVPN installation is ready to begin."
        # Install a firewall in the rare case where one is not already available
        if ! systemctl is-active --quiet firewalld.service && ! hash iptables 2>/dev/null; then
                if [[ "$os" == "centos" || "$os" == "fedora" ]]; then
                        firewall="firewalld"
                        # We don't want to silently enable firewalld, so we give a subtle warning
                        # If the user continues, firewalld will be installed and enabled during setup
                        echo "firewalld, which is required to manage routing tables, will also be installed."
                elif [[ "$os" == "debian" || "$os" == "ubuntu" ]]; then
                        # iptables is way less invasive than firewalld so no warning is given
                        firewall="iptables"
                fi
        fi
        read -n1 -r -p "Press any key to continue..."
        # If running inside a container, disable LimitNPROC to prevent conflicts
        if systemd-detect-virt -cq; then
                mkdir /etc/systemd/system/openvpn-server@server.service.d/ 2>/dev/null
                echo "[Service]
LimitNPROC=infinity" > /etc/systemd/system/openvpn-server@server.service.d/disable-limitnproc.conf
        fi
        if [[ "$os" = "debian" || "$os" = "ubuntu" ]]; then
                apt-get update
                apt-get install -y openvpn openssl ca-certificates $firewall python3 python3-pip
        elif [[ "$os" = "centos" ]]; then
                yum install -y epel-release
                yum install -y openvpn openssl ca-certificates tar $firewall python3 python3-pip
        else
                # Else, OS must be Fedora
                dnf install -y openvpn openssl ca-certificates tar $firewall python3 python3-pip
        fi
        # If firewalld was just installed, enable it
        if [[ "$firewall" == "firewalld" ]]; then
                systemctl enable --now firewalld.service
        fi
        # Get easy-rsa
        easy_rsa_url='https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.8/EasyRSA-3.0.8.tgz'
        mkdir -p /etc/openvpn/server/easy-rsa/
        { wget -qO- "$easy_rsa_url" 2>/dev/null || curl -sL "$easy_rsa_url" ; } | tar xz -C /etc/openvpn/server/easy-rsa/ --strip-components 1
        chown -R root:root /etc/openvpn/server/easy-rsa/
        cd /etc/openvpn/server/easy-rsa/
        # Create the PKI, set up the CA and the server and client certificates
        ./easyrsa init-pki
        ./easyrsa --batch build-ca nopass
        EASYRSA_CERT_EXPIRE=3650 ./easyrsa build-server-full server nopass
        EASYRSA_CERT_EXPIRE=3650 ./easyrsa build-client-full "$client" nopass
        EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
        # Move the stuff we need
        cp pki/ca.crt pki/private/ca.key pki/issued/server.crt pki/private/server.key pki/crl.pem /etc/openvpn/server
        # CRL is read with each client connection, while OpenVPN is dropped to nobody
        chown nobody:"$group_name" /etc/openvpn/server/crl.pem
        # Without +x in the directory, OpenVPN can't run a stat() on the CRL file
        chmod o+x /etc/openvpn/server/
        # Generate key for tls-crypt
        openvpn --genkey --secret /etc/openvpn/server/tc.key
        # Create the DH parameters file using the predefined ffdhe2048 group
        echo '-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA//////////+t+FRYortKmq/cViAnPTzx2LnFg84tNpWp4TZBFGQz
+8yTnc4kmz75fS/jY2MMddj2gbICrsRhetPfHtXV/WVhJDP1H18GbtCFY2VVPe0a
87VXE15/V8k1mE8McODmi3fipona8+/och3xWKE2rec1MKzKT0g6eXq8CrGCsyT7
YdEIqUuyyOP7uWrat2DX9GgdT0Kj3jlN9K5W7edjcrsZCwenyO4KbXCeAvzhzffi
7MA0BM0oNC9hkXL+nOmFg/+OTxIy7vKBg8P+OxtMb61zO7X8vC7CIAXFjvGDfRaD
ssbzSibBsu/6iGtCOGEoXJf//////////wIBAg==
-----END DH PARAMETERS-----' > /etc/openvpn/server/dh.pem
        # Generate server.conf
        echo "local $ip
port $port
proto $protocol
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
auth SHA512
tls-crypt tc.key
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt" > /etc/openvpn/server/server.conf

        pusg_route=y
        while [[ $pusg_route == "y" ]]; do
                read  "add vpn route[x.x.x.x x.x.x.x]" route
                if [[ "$route" ]]; then
                        echo 'push "route '$route' vpn_gateway"' >> /etc/openvpn/server/server.conf
                fi
                read  "is add route[x|y]" pusg_route
                #statements
        done

        echo "keepalive 10 120
cipher AES-256-CBC
user nobody
group $group_name
persist-key
persist-tun
status openvpn-status.log
verb 3
crl-verify crl.pem
script-security 3
client-connect \"/usr/local/bin/openvpn_shell.sh connect\"
client-disconnect \"/usr/local/bin/openvpn_shell.sh disconnect\"
auth-user-pass-verify \"/usr/local/bin/openvpn_shell.sh check_user\" via-env" >> /etc/openvpn/server/server.conf
        if [[ "$protocol" = "udp" ]]; then
                echo "explicit-exit-notify" >> /etc/openvpn/server/server.conf
        fi
        # Enable net.ipv4.ip_forward for the system
        echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/30-openvpn-forward.conf
        # Enable without waiting for a reboot or service restart
        echo 1 > /proc/sys/net/ipv4/ip_forward
        if [[ -n "$ip6" ]]; then
                # Enable net.ipv6.conf.all.forwarding for the system
                echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.d/30-openvpn-forward.conf
                # Enable without waiting for a reboot or service restart
                echo 1 > /proc/sys/net/ipv6/conf/all/forwarding
        fi
        if systemctl is-active --quiet firewalld.service; then
                # Using both permanent and not permanent rules to avoid a firewalld
                # reload.
                # We don't use --add-service=openvpn because that would only work with
                # the default port and protocol.
                firewall-cmd --add-port="$port"/"$protocol"
                firewall-cmd --zone=trusted --add-source=10.8.0.0/24
                firewall-cmd --permanent --add-port="$port"/"$protocol"
                firewall-cmd --permanent --zone=trusted --add-source=10.8.0.0/24
                # Set NAT for the VPN subnet
                firewall-cmd --direct --add-rule ipv4 nat POSTROUTING 0 -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to "$ip"
                firewall-cmd --permanent --direct --add-rule ipv4 nat POSTROUTING 0 -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to "$ip"
                if [[ -n "$ip6" ]]; then
                        firewall-cmd --zone=trusted --add-source=fddd:1194:1194:1194::/64
                        firewall-cmd --permanent --zone=trusted --add-source=fddd:1194:1194:1194::/64
                        firewall-cmd --direct --add-rule ipv6 nat POSTROUTING 0 -s fddd:1194:1194:1194::/64 ! -d fddd:1194:1194:1194::/64 -j SNAT --to "$ip6"
                        firewall-cmd --permanent --direct --add-rule ipv6 nat POSTROUTING 0 -s fddd:1194:1194:1194::/64 ! -d fddd:1194:1194:1194::/64 -j SNAT --to "$ip6"
                fi
        else
                # Create a service to set up persistent iptables rules
                iptables_path=$(command -v iptables)
                ip6tables_path=$(command -v ip6tables)
                # nf_tables is not available as standard in OVZ kernels. So use iptables-legacy
                # if we are in OVZ, with a nf_tables backend and iptables-legacy is available.
                if [[ $(systemd-detect-virt) == "openvz" ]] && readlink -f "$(command -v iptables)" | grep -q "nft" && hash iptables-legacy 2>/dev/null; then
                        iptables_path=$(command -v iptables-legacy)
                        ip6tables_path=$(command -v ip6tables-legacy)
                fi
                echo "[Unit]
Before=network.target
[Service]
Type=oneshot
ExecStart=$iptables_path -t nat -A POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $ip
ExecStart=$iptables_path -I INPUT -p $protocol --dport $port -j ACCEPT
ExecStart=$iptables_path -I FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStart=$iptables_path -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
ExecStop=$iptables_path -t nat -D POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $ip
ExecStop=$iptables_path -D INPUT -p $protocol --dport $port -j ACCEPT
ExecStop=$iptables_path -D FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStop=$iptables_path -D FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT" > /etc/systemd/system/openvpn-iptables.service
                if [[ -n "$ip6" ]]; then
                        echo "ExecStart=$ip6tables_path -t nat -A POSTROUTING -s fddd:1194:1194:1194::/64 ! -d fddd:1194:1194:1194::/64 -j SNAT --to $ip6
ExecStart=$ip6tables_path -I FORWARD -s fddd:1194:1194:1194::/64 -j ACCEPT
ExecStart=$ip6tables_path -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
ExecStop=$ip6tables_path -t nat -D POSTROUTING -s fddd:1194:1194:1194::/64 ! -d fddd:1194:1194:1194::/64 -j SNAT --to $ip6
ExecStop=$ip6tables_path -D FORWARD -s fddd:1194:1194:1194::/64 -j ACCEPT
ExecStop=$ip6tables_path -D FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT" >> /etc/systemd/system/openvpn-iptables.service
                fi
                echo "RemainAfterExit=yes
[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/openvpn-iptables.service
                systemctl enable --now openvpn-iptables.service
        fi
        # If SELinux is enabled and a custom port was selected, we need this
        if sestatus 2>/dev/null | grep "Current mode" | grep -q "enforcing" && [[ "$port" != 1194 ]]; then
                # Install semanage if not already present
                if ! hash semanage 2>/dev/null; then
                        if [[ "$os_version" -eq 7 ]]; then
                                # Centos 7
                                yum install -y policycoreutils-python
                        else
                                # CentOS 8 or Fedora
                                dnf install -y policycoreutils-python-utils
                        fi
                fi
                semanage port -a -t openvpn_port_t -p "$protocol" "$port"
        fi
        # If the server is behind NAT, use the correct IP address
        [[ -n "$public_ip" ]] && ip="$public_ip"
        # client-common.txt is created so we have a template to add further users later
        echo "client
dev tun
proto $protocol
remote $ip $port
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
cipher AES-256-CBC
ignore-unknown-option block-outside-dns
block-outside-dns
verb 3" > /etc/openvpn/server/client-common.txt
        # Enable and start the OpenVPN service
        systemctl enable --now openvpn-server@server.service
        pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r $MYDIR/requirements.txt
        cd  $MYDIR
        python3 manage.py makemigrations
        python3 manage.py migrate
        chmod 755 $MYDIR/start.sh
        $MYDIR/start.sh start 
fi

