#!/bin/zsh
PATH=$PATH:/usr/bin
content=$(curl -s "https://www.superanimes.site/anime/$1")

total=$(echo $content | awk '/<strong>Ep/{gsub(/[^0-9]/,"");print}')
echo "Total de episódios: $total"

if echo $content | grep -q "não foi encontrada"; then
	echo "O anime não existe"
	exit 1
fi

if [ $2 = "--one" ] || [ $2 = "-o" ] ; then
	wget -q $(curl -s https://www.superanimes.site/anime/$1/episodio-$3/baixar  | sed -e '/bt-download/!d' -e 's/.*href="//' -e 's/".*//')  --show-progress -O $1-$3.mp4
	exit 0
fi

for i in {1..$total} ; do 
	wget -q $(curl -s https://www.superanimes.site/anime/$1/episodio-$i/baixar  | sed -e '/bt-download/!d' -e 's/.*href="//' -e 's/".*//')  --show-progress -O $1-$i.mp4
done
