#!/bin/sh

# Configuration du proxy pour apt
FILE="/etc/apt/apt.conf"

/bin/cat <<EOM >$FILE
Acquire::http::proxy "http://username:password@proxy_host:proxy_port";
Acquire::ftp::proxy "ftp://username:password@proxy_host:proxy_port";
Acquire::https::proxy "https://username:password@proxy_host:proxy_port";
EOM

# Configuration du proxy pour wget
FILE="/etc/wgetrc"

/bin/cat <<EOM >$FILE
http_proxy = http://username:password@proxy_host:proxy_port
https_proxy = https://username:password@proxy_host:proxy_port
EOM

# Configuration du proxy pour ssh
apt-get install -y corkscrew
FILE="/root/.ssh/.proxy-auth"
/bin/cat <<EOM >$FILE
username:password
EOM

FILE="/root/.ssh/config"
/bin/cat <<EOM >$FILE
Host github.com
  Hostname ssh.github.com
  Port 443
  ProxyCommand corkscrew proxy_host proxy_port %h %p /root/.ssh/.proxy-auth
EOM

# Installation de Git
apt-get install -y git

# Configuration du proxy pour Git (modifie ~/.gitconfig)
export HTTP_PROXY=http://username:password@proxy_host:proxy_port
export HTTPS_PROXY=https://username:password@proxy_host:proxy_port
git config --global http.proxy $HTTP_PROXY
git config --global https.proxy $HTTPS_PROXY

apt-get update
apt-get -y install wget
apt-get -y install python2.7
apt-get -y install python-dev
apt-get -y install gcc

curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
chmod +x get-pip.py
python get-pip.py --proxy=$http_proxy

pip install Fabric==1.13.1
pip install PyYAML==3.12
