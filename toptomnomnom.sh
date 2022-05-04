#!/bin/bash

#install golang
sudo apt install golang
# You may change GOPATH this script uses ~/go/. Other tools - amass, finddomain.

# anew => cat newthings.txt | anew things.txt (add new things without duplicating existing things)
# httprobe => cat domains.txt | httprobe -p http:81 https:8443 (Check alive hosts)
# fff => cat urls.txt | fff [-x : proxy] (make request to server damn fast and route them through proxy)
# meg => meg --verbose paths hosts (get every path to each hosts - its nice to server and better than fff)
# waybackurls => cat domains.txt | waybackurls > urls (It gets old version of perticular domain using Internet archive - archive.org)
# gf => (grep format # edit gf patterns at ~/.gf & add auto completion in sources of bash/zsh "source ~/path/to/gf-completion.bash" )
# comb => comb [OPTIONS] <prefixfile> <suffixfile> (Combine the lines from two files in every combination)
# qsreplace => cat urls.txt | qsreplace newval (replace query strings with another)
# assetfinder => assetfinder [--subs-only] <domain> (Find domains related to domains using passive methods)
# gron => gron --json testdata/two.json | grep likes | gron  --json --ungron (It makes json grep-able and vice-versa)
# unfurl => cat urls.txt | unfurl domains (extract domain from a list of URLs)


for tool in anew httprobe fff meg gf waybackurls gron comb qsreplace assetfinder;
do
    echo "[i] installing $tool"
    go install -v github.com/tomnomnom/$tool@latest ; sudo mv ~/go/bin/$tool /opt/. ; sudo chmod +x /opt/$tool ; 
    echo "alias $tool=\"/opt/$tool\"" >> ~/.bashrc ; echo "alias $tool=\"/opt/$tool\"" >> ~/.zshrc
    # or export PATH=$PATH:/opt
    echo "[i] installed $tool"
    # to remove these tools from your system
    #sudo rm /opt/$tool
done;
