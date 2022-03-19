# Beginner-Bug-Bounty-Automation
These scripts are designed to be painkiller for initial bug bounty hunting stages & based on top bug hunter's methadology around the world.
[Under Construction, Check back soon!]

## Clone this repo before proceeding
`git clone https://github.com/sam5epi0l/Beginner-Bug-Bounty-Automation ; cd Beginner-Bug-Bounty-Automation || exit`
#### All binaries, repos, and wordlists will be stored at /opt/ Directory

- ## 1. tor-gateway.sh (It's like anonsurf on any Linux distro)
This script uses nipe to make TOR, the default gateway of your computer.
### [Video Tutorial](https://youtu.be/kqNwJWdI1xM)
Install:
```
chmod +x tor-gateway.sh
./tor-gateway.sh
# type sudo's password
# type "yes" to continue
```
Uses:
```
# Start nipe (TOR-gateway)
nipe start

# Check status
nipe status

# Stop nipe
nipe stop

# restart service
nipe restart
```

- ## 2. toptomnomnom.sh
Install top useful tools from [Tom Hudson's](https://github.com/tomnomnom/) github repo.
How to use:
```
chmod +x toptomnomnom.sh
# Install tools
./toptomnomnom.sh
# to uninstall one or more tools visit the script :)
```

- ## 3. bug-bounty-essentials.sh
Install essential tools required during Bug Hunting for Reconnaissance
How to use:
```
chmod +x bug-bounty-essentials.sh
Install essential tools
./bug-bounty-essentials.sh
```
