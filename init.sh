#!/bin/bash

echo "automating that youtube video"
echo "I assume you're in recon folder"
echo "it should contain a wildcards.txt file"

wildcard=$(cat wildcards.txt)
lines=$(echo "$wildcard" | wc -l)

for ((i=0; i<lines; i++))
do
    wc=$(echo "$wildcard" | sed -n "$((i+1)) p")
    echo "[i] recon started for $wc"
    #amass enum -passive -d "$wc" -o amass_passive.txt
    echo "[i] amass passive recon done for $wc"
    echo
    echo "[i] finding new domains with findomain"
    findomain -f "wildcards.txt" | tee -a findomain.txt | anew domains.txt
    echo
done

echo "[i] add these to domain.txt file and remove duplicates"
anew domains.txt < amass_passive.txt
echo

echo "[i] search domains on archive.org"
# or use gau
waybackurls < domains.txt | tee waybackurls.txt
echo

echo "[i] looking for alive waybackurls with httpx"
httpx -o alive-waybackurls.txt < waybackurls.txt
echo

echo "[i] Filtering Live hosts to alive_domain.txt (default rate concurrency is 10)"



httprobe -c 10 < domains.txt | anew alive-host.txt
echo

echo "[i] Let' request all URLs with fff"
fff -d 5000 -S -o roots_fff < alive-host.txt
echo


echo "[i] Use meg to send same path request to all"
meg paths.txt alive-hosts.txt roots_meg
echo

echo "[i] fetching gf output for alive-waybackurls.txt"
mkdir gf-patterns

for a in ~/.gf/*.json; do
echo "$a" | cut -d "/" -f5 | cut -d "." -f1 | read -r bug
cat alive-waybackurls.txt | gf $bug > gf-patterns/alive-waybackurls-$bug.txt && echo "[i] gf output for $bug saved in gf-patterns/alive-waybackurls-$bug.txt"
done
