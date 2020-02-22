import re
import csv
import requests
from bs4 import BeautifulSoup
from random import choice
# from . import edit_fields
COUNTER = 0



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
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    # r = requests.get(url)
    # r = requests.get(url, proxies=proxy)
    r = requests.get(url, headers=user_agent)
    return r.content if r.ok else print('Status Code:',r.status_code)


def get_categories(url):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  links = soup.find('div', {'class':'sitemap-info'}).find('div', class_='left').find_all('a')
  for link in links[318:]:
    cat_name = link.text
    url = link.get('href')+'?limit=10000'
    try:get_products(url, cat_name)
    except Exception as e: print(e)    
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_products(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  cat_name = args[0]
  products = soup.find_all('div', class_='product-thumb')
  for product in products:
    link = product.find('div', class_='image').a.get('href')
    get_product(link, cat_name)
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_product(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  category = args[0]
  name  = soup.h1.text.strip()
  price_raw = soup.find_all('h2')[1].text.strip().split(' ')
  price = price_raw[0]
  currency = price_raw[1]
  desc = '\n'.join(str(soup.find('div', id='tab-description')).split('</p>'))\
    # .replace('<p>','')\
    # .replace('<br/>', '')\
    # .replace('<b>','')\
    # .replace('</b>', '')\
    # .replace('</div>','')
  # desc = re.sub(r'\<div[^>]*\ >', '', desc)
  desc = re.sub('<[^>]+>', '', desc)
  img = []
  for i in soup.find_all('a', class_='thumbnail'):
    img.append(i.get('href'))
  img = ', '.join(img)
  # lis = soup.find_all('li')
  # for li in lis:
  #   try:
  #     element = li.text.strip().split(' ')
  #     print(element)
  #     if element[0] == "Производитель":
  #       manufacturer = element[1]
  #       print(manufacturer)
  #   except: manufacturer = ''
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  data = {
    # основные поля
    'articule':'',
    'name':name,
    'searches':'',
    'desc':desc,
    'type':'r',
    'price':price,
    'price_from':'',
    'currency': currency,
    'measurment_unit':"шт",
    'minimum':'', 'wholesale':'', 'minimums_wholesale':'', 'amount':'',     
    'img':img,
    'avaliable':'+',#avaliable,      
    'action':'', 'action_from':'', 'action_to':'', 'label':'',
    'manufacturer':'',
    'country':'', 
    'HTML_header':'', 'HTML_description':'', 'HTML_keywords':'', 
    'gifts':'', 'group_number':'', 'group_name':'', 'subsection_address':'', 
    'delivery_possibility':'', 'delivery_terms':'', 'packing':'', 'personal_notes':'',
    'product_link':url,
    'GTIN':'', 'MPN':'',
    'product_id':'',
    'product_unique_id':'', 'subsection_id':'',
    'group_id':category,
    'species_group_id':'',
    
    # характеристики

    # Название_Характеристики   
    # Измерение_Характеристики   
    # Значение_Характеристики


  }
  global COUNTER; COUNTER += 1
  print(COUNTER)
  print(name)
  print(category)
  print(url)
  # print(desc)
  write_csv(data)


def write_csv(data):
  with open('raw_korvet.csv', 'a') as f:
      # order = [
      #   'name', 'price', 'desc', 
      #   'cat', 'subcat', 'link', 
      #   'img_name', 'img_link'
      # ]
      order = list(data.keys())
      writer = csv.DictWriter(f, fieldnames=order)
      writer.writerow(data)


def cats():
  from links import links
  for link in links:
    get_products(link[0], link[1])



if __name__ == '__main__':
  cats()
  # get_product('https://korvet-m.com.ua/index.php?route=product/product&product_id=348', 'Стальные топки')
  # edit_fields()