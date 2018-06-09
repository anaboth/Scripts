from bs4 import BeautifulSoup
import requests
from urllib.request import urlretrieve
import threading
import time

def download_page(index):
    try:
        html = requests.get(f'https://wallpapersmug.com/w/wallpaper/tag/anime/page/{index}').text
    except:
        time.sleep(2)
        try:
            html = requests.get(f'https://wallpapersmug.com/w/wallpaper/tag/anime/page/{index}').text
        except:
            time.sleep(2)
            html = requests.get(f'https://wallpapersmug.com/w/wallpaper/tag/anime/page/{index}').text
    parsed = BeautifulSoup(html, 'lxml')
    elements = parsed.findAll('div', attrs={'class': 'col-md-3 col-sm-4 col-xs-6'})
    for i in elements:
        url = 'https://wallpapersmug.com' + i.a.get('href') + '/download'
        print(url)
        try:
            img_page = requests.get(url).text
        except:
            time.sleep(2)
            try:
                img_page = requests.get(url).text
            except:
                time.sleep(2)
                img_page = requests.get(url).text
        parsed = BeautifulSoup(img_page, 'lxml')
        dl_link = parsed.find('a', attrs={'class': 'btn btn-primary'}).get('href')
        print(dl_link)
        name = dl_link.split('/')[5]
        print(name)
        try:
            r = requests.get(dl_link, stream=True)
        except:
            time.sleep(2)
            try:
                r = requests.get(dl_link, stream=True)
            except:
                time.sleep(2)
                r = requests.get(dl_link, stream=True)
        with open(name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

for i in range(1, 109):
    t = threading.Thread(target=download_page, args=[i])
    t.start()
