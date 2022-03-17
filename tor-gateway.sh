#!/bin/bash

# install apt repos
sudo apt update && sudo apt install perl tor -y
echo .........................................................................................................
# Download
cd /opt || exit ; sudo git clone https://github.com/htrgouvea/nipe ; cd nipe || exit;
echo .........................................................................................................

# Install libs and dependencies
sudo cpan install Try::Tiny Config::Simple JSON
echo .........................................................................................................

# Nipe must be run as root
perl nipe.pl install
echo .........................................................................................................

# add launcher
echo sudo perl nipe.pl \$1 | sudo tee nipe
echo .........................................................................................................

sudo chmod +x nipe.pl nipe
echo .........................................................................................................

# create symbolic link
sudo ln -sf /opt/nipe/nipe /usr/bin/nipe.pl
echo .........................................................................................................

# start / stop / restart
nipe.pl
echo .........................................................................................................
echo "just run nipe.pl start from terminal to start TOR"
