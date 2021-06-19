# http://91porn.com/v.php?next=watch&page=
import requests
import parsel
import arrow
import os
from tqdm import tqdm
from config import *

arw = arrow.utcnow()
items = ''
flag = 0


def get_response(html_url):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'Cookie': COOKIE,
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Host': '91porn.com',
        'Referer': 'http://91porn.com/index.php',
        'Upgrade-Insecure-Requests': '1',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    response = requests.get(url=html_url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def get_content(html_url, title, fav_count):
    global items
    response = get_response(html_url)
    selector = parsel.Selector(response.text)
    UID = selector.css('#favorite>#UID::text').get()
    VID = selector.css('#favorite>#VID::text').get()
    VUID = selector.css('#favorite>#VUID::text').get()
    items = items + VID + '\n'
    if fav_count > FAVORITES:
        print(f'{title} 收藏量: {fav_count}')
    if IF_FAVORITE:
        handle_fav = get_response(
            f'http://91porn.com/add_favorite.php?VID={VID}&UID={UID}&VUID={VUID}'
        )
        if handle_fav.status_code == 200:
            print(f'{title} 收藏成功！收藏量: {fav_count}')


def get_page(html_url):
    global flag
    response = get_response(html_url)
    selector = parsel.Selector(response.text)
    articles = selector.css('.row>div').getall()
    for article in tqdm(articles):
        selector = parsel.Selector(article)
        title = selector.css('.video-title::text').get()
        url = selector.css('.well>a::attr(href)').get()
        strs = selector.css('.well *::text').getall()
        tm = strs[strs.index('添加时间:') + 1].replace(' ', '')
        tms = arw.dehumanize(tm, locale='zh-cn')
        fav_count = int(strs[strs.index('收藏:') + 1].strip())
        if (arw.int_timestamp - tms.int_timestamp) / 3600 < HOUR_AGO:
            get_content(url, title, fav_count)
            continue
        else:
            flag = 1
            break


if __name__ == '__main__':
    for p in range(1, PAGE):
        url = f'http://91porn.com/v.php?next=watch&page={p}'
        print(f'开始扫描第{p}页')
        if flag == 1:
            break
        else:
            get_page(url)
            continue
    with open(f"{os.getcwd()}/91/result.txt", "w", encoding='utf-8') as f:
        f.write(items)