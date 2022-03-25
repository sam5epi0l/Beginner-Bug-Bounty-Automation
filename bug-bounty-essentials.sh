#!/bin/bash

# install all tomnomtools.
echo "[-] This script requires toptomnomnom.sh"
bash toptomnomnom.sh
echo "[-] Installing snapd"
sudo apt install snapd
sudo systemctl start snapd.service

# install gf-patterns with auto completion
sudo rm /usr/bin/gf; sudo mv /opt/gf /opt/gff; sudo mkdir /opt/gf/; sudo mv /opt/gff /opt/gf/gf;
cd /opt/gf/ || exit ; sudo wget https://raw.githubusercontent.com/tomnomnom/gf/master/gf-completion.bash ; sudo wget https://raw.githubusercontent.com/tomnomnom/gf/master/gf-completion.zsh ;
sudo chmod +x /opt/gf/gf ; sudo ln -sf /opt/gf/gf /usr/bin/gf ;
echo 'source /opt/gf/gf-completion.bash' >> ~/.bashrc
echo 'source /opt/gf/gf-completion.zsh' >> ~/.zshrc

echo "[i] All Requirements installed."
# amass => amass enum -passive -d owasp.org -src (amass [subcommands] [options] -d host)
#go install -v github.com/owasp/amass@latest ; sudo mv ~/go/bin amass /opt/. ; sudo chmod +x /opt/amass ; sudo ln -sf /opt/amass /usr/bin/amass
echo "[i] Installing amass"
sudo snap install amass
# sudo rm /opt/amass /usr/bin/amass

# Insall finddomain which get newly registered domains on target
echo "[i] Installing findomain"
sudo wget https://github.com/findomain/findomain/releases/latest/download/findomain-linux ; sudo mv findomain-linux /opt/findomain ; sudo chmod +x /opt/findomain ; sudo ln -sf /opt/findomain /usr/bin/findomain
# sudo rm /opt/findomain /usr/bin/findomain

echo "[i] Installing go tools"
#other tools from projectdiscovery are subfinder, naabu, nuclei, dnsx

# Install httpsx which is updated and better than httprobe
echo "[i] Installing httpx"
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest ; sudo mv ~/go/bin/httpx /opt/. ; sudo chmod +x /opt/httpx ; sudo ln -sf /opt/httpx /usr/bin/httpx
echo "[i] installed httpx"
