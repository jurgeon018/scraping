import re
import csv
import requests
from bs4 import BeautifulSoup
from random import choice


def get_proxy():
    html = requests.get('https://free-proxy-list.net/').text
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find('table', id='proxylisttable').find_all('tr')[50:100]
    proxies = []
    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        schema = 'https' if 'yes' in tds[6].text.strip() else 'http'
        proxy = {'schema': schema, 'address': ip + ':' + port}
        proxies.append(proxy)
    return choice(proxies)


def get_html(url):
    p = get_proxy()
    proxy = { p['schema']: p['address']  }
    # print(proxy)
    # r = requests.get(url, proxies=proxy)
    r = requests.get(url)
    return r.text if r.ok else print(r.status_code)


def write_csv(data):
  with open('ukrchic.csv', 'a') as f:
      order = ['name', 'price', 'desc', 'cat', 'subcat', 'link', 'img_name', 'img_link']
      writer = csv.DictWriter(f, fieldnames=order)
      writer.writerow(data)


def get_product(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  buttons = soup.find('div', class_='grid_8').find_all('div', class_='nicdark_margin05')
  cat = buttons[1].text.strip()
  subcat = buttons[2].text.strip() if len(buttons) == 4 else cat
  name = soup.h1.text
  price = soup.h2.text
  desc  = soup.find_all('p')[-2].text
  return {
    'cat':cat,
    'subcat':subcat,
    'name':name,
    'price':price,
    'desc':desc
  }


def many(html, *args, **kwargs):
    soup = BeautifulSoup(get_html(html), 'lxml')
    products = soup.find_all('div', class_='nicdark_archive1 nicdark_border_grey')
    i = 0
    for product in products:
      i += 1
      print(i)
      link = 'http://tkani.ukrchic.com/'+product.a.get('href')
      try: img_link = product.a.get('style').split('background: url')[1].split(' ')[0][1:-1]
      except: img_link = ''
      img_name = link.split('/')[-1]+'.jpeg'
      name = get_product(link)['name']
      cat = get_product(link)['cat']
      subcat = get_product(link)['subcat']
      price = get_product(link)['price']
      desc = get_product(link)['desc']
      with open(f"{img_name}", "wb") as out:
        try: out.write(requests.get(img_link).content)
        except: pass
      data = {
        'name':name,
        'price':price,
        'desc':desc,
        'cat':cat,
        'subcat':subcat,
        'link':link,
        'img_name':img_name,
        'img_link':img_link,
      }
      print(name)
      write_csv(data)

def get_cat(url):
  soup = BeautifulSoup(get_html(html), 'lxml')
  cats = soup.
def main():
  get_cat('http://tkani.ukrchic.com/')
  # many('http://tkani.ukrchic.com/products?page=all')
  # get_product('http://tkani.ukrchic.com/products/kruzhevo-11518-10l-ivory-m')
  # get_product('http://tkani.ukrchic.com/products/pajetka-zolotaya-100g')
  
if __name__ == '__main__':
    main()
