#!/bin/zsh

echo "\e[38;5;82m256 term colors\e[0m\n"

for color in {0..256} ; do
    echo -en "\e[38;5;${color}m$(printf "%03d" ${color})\t\e[0m"
    if [[ $((($color + 1) % 10)) == 0 ]] ; then
		echo; fi
done; echo; exit 0
