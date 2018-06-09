# -*- coding: utf-8 -*-
import requests
import curses
import threading
import os
import time
import argparse
import unicodedata
from bs4 import BeautifulSoup
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message', type=str, help='Download message to be displayed on top of the screen')
parser.add_argument('-j', '--jobs', type=int, help='Number of jobs to run in parallel')
parser.add_argument('-s', '--search-only', action='store_true', help='When set, will only search and print the results')
parser.add_argument('--start', type=int, help='Episode number to start download')
parser.add_argument('--end', type=int, help='Episode number to end download')
parser.add_argument('search', type=str, help='Search content')
args = parser.parse_args()


print_lock = threading.Lock()
downloadLinks = []
if args.message:
    downloading_phrase = args.message
else:
    downloading_phrase = 'Downloading'
html = requests.get(f'https://www.superanimes.site/busca?parametro={args.search}').text
parsed = BeautifulSoup(html, 'lxml')
list_animes = parsed.body.findAll('div', attrs={'class': 'boxLista2'})
real_animes = []
i = 0


class Anime(object):
    def __init__(self, param):
        self.name = param['Nome']
        self.token = param['token']
        self.episodes_quantity = int(param['Total de Vídeos'])
        self.genre = param['Gênero']
        self.author = param['Autor']
        self.studio = param['Estúdio']
        self.classification = param['Classificação']
        self.threshold = param['threshold']
        self.episodes_links = []
        try:
            self.alternative_name = param['Nome Alternativo']
        except:
            self.alternative_name = ''


def normalize(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def download(name, ep, url, threshold):
    try:
        video = requests.get(url, stream=True)
    except:
        time.sleep(2)
        video = requests.get(url, stream=True)
    total_size = int(video.headers['content-length'])
    chunk_size = 1024
    dl = 0
    home = str(Path.home())
    try:
        os.mkdir(f'{home}/Animes')
    except:
        pass
    try:
        os.mkdir(f'{home}/Animes/{name}')
    except:
        pass
    with open(f'{home}/Animes/{name}/{name} - {ep}.mp4', 'wb') as file:
        for data in video.iter_content(chunk_size=chunk_size):
            dl += len(data)
            file.write(data)
            done = int(50 * dl / total_size)
            rows, columns = os.popen('stty size', 'r').read().split()
            if threshold + ep < int(rows):
                with print_lock:
                    curse.addstr(0,0, ' ' * (int(columns)-1))
                    curse.addstr(0, round((int(columns) / 2) - len(downloading_phrase) / 2), downloading_phrase)
                    curse.addstr(threshold + ep, 0,
                        f'{name} - ep{ep}{" " * (int(columns) - 58 - len(name) - len(str(ep)))}[{"=" * done}{" " * (50 - done)}]')
                    curse.refresh()


def get_download_link(anime, ep):
    try:
        anime_page = requests.get(f'https://www.superanimes.site/anime/{anime.token}/episodio-{ep}/baixar').text
    except:
        time.sleep(2)
        anime_page = requests.get(f'https://www.superanimes.site/anime/{anime.token}/episodio-{ep}/baixar').text
    anime_page = BeautifulSoup(anime_page, 'lxml')
    link = anime_page.find('a', attrs={'class': 'bt-download'}).get('href')
    anime.episodes_links.append({'ep': ep, 'link': link})


def get_download_link_all(anime):
    for ep in range(1, anime.episodes_quantity+1):
        try:
            anime_page = requests.get(f'https://www.superanimes.site/anime/{anime.token}/episodio-{ep}/baixar').text
        except:
            time.sleep(2)
            anime_page = requests.get(f'https://www.superanimes.site/anime/{anime.token}/episodio-{ep}/baixar').text
        anime_page = BeautifulSoup(anime_page, 'lxml')
        link = anime_page.find('a', attrs={'class': 'bt-download'}).get('href')
        anime.episodes_links.append({'ep': ep, 'link': link})


for anime in list_animes:
    contents = anime.findAll('div', attrs={'class': 'boxLista2Nome'})
    buffer = {}
    for content in contents:
        try:
            strings = content.text.split(':')
            buffer[strings[0].strip()] = strings[1].strip()
        except:
            try:
                buffer['Nome'] = content.a.h2.text
            except:
                buffer['Classificação'] = content.span.text
    buffer['token'] = contents[0].a.get('href').split('/')[4]
    try:
        buffer['threshold'] = real_animes[i-1].episodes_quantity + real_animes[i-1].threshold
    except:
        buffer['threshold'] = 0
    i += 1
    x = Anime(buffer)
    real_animes.append(x)

if args.search_only:
    for anime in real_animes:
        print(f'\nName: {anime.name}\nEPS: {anime.episodes_quantity}\n')
    exit(0)


for anime in real_animes:
    start = args.start if args.start else 1
    end = args.end + 1 if args.end else anime.episodes_quantity + 1
    for i in range(start, end):
        t = threading.Thread(target=get_download_link, args=(anime, i))
        t.start()
    
while threading.active_count() != 1:
    time.sleep(1)

for anime in real_animes:
    for i in anime.episodes_links:
        downloadLinks.append([anime.name, int(i['ep']), i['link'], anime.threshold])

curse = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
curse.clear()
curse.refresh()

for i in downloadLinks:
    if args.jobs:
        while threading.active_count() >= args.jobs + 1:
            time.sleep(2)
    t = threading.Thread(target=download, args=i)
    t.start()

curses.endwin()
