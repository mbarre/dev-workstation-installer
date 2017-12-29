# Developer workstation install script

Python script that installs all development tools (and more...) I need to work on my Linux Mint workstation.

## Requirements

### Wget

```
sudo apt-get install wget
```

### Python

```
sudo apt-get install python2.7
sudo apt-get install -y gcc
```

### Pip

```
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo chmod +x get-pip.py
sudo ./get-pip.py
```

### Fabric

```
sudo pip install Fabric==1.13.1
sudo pip install PyYAML==3.12
```