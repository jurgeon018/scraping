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
    r = requests.get(url)#, proxies=proxy)
    return r.text if r.ok else print(r.status_code)


def get_categories(url):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  links = soup.find('div', class_='cpt_category_tree').find_all('a')[2:]
  for link in links:
    cat_name = ' '.join(link.text.strip().split())
    url = "https://apexlab.ru"+link.get('href')+'all'
    # print(url)
    print(cat_name)
    # print('***')
    # get_products(url, cat_name)
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_products(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  cat_name = args[0]
  print(url)
  products = soup.find_all('a', class_='one_product_desc')
  for product in products:
    url = "https://apexlab.ru" + product.get('href')
    get_product(url, cat_name)
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_product(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  print(url)
  category = args[0]
  name  = soup.find('div', class_="cpt_product_name").text
  desc  = soup.find('div', class_='cpt_product_description').text
  price = soup.find('div', class_='cpt_product_price').text.strip()
  img   = "https://apexlab.ru" + soup.find('img', id='img-current_picture').get('src')
  # img = []
  # for i in soup.find_all('a', class_='fancybox'):
  #   img.append(i.get('href'))
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  print(name)
  data = {
    # основные поля
    'articule':'',
    'name':name,
    'searches':'',
    'desc':desc,
    'type':'r',
    'price':price,
    'price_from':'',
    'currency': 'RUB',
    'measurment_unit':"шт",
    'minimum':'', 'wholesale':'', 'minimums_wholesale':'', 'amount':'',     
    'img':[i for i in img] or img,
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
  # write_csv(data)


def write_csv(data):
  with open('raw_remza.csv', 'a') as f:
      # order = [
      #   'name', 'price', 'desc', 
      #   'cat', 'subcat', 'link', 
      #   'img_name', 'img_link'
      # ]
      order = list(data.keys())
      writer = csv.DictWriter(f, fieldnames=order)
      writer.writerow(data)





def cats():
  get_products(url2)
  url2 = 'https://www.blezer.ru/discounted/' + '?limit=10000'
  get_products(url2)

def solo():
  get_product(url)

def main():
  # get_categories('https://apexlab.ru/')
  get_categories('https://apexlab.ru/category/instrumenty-dla-mikrobiology/')
  


if __name__ == '__main__':
  main()
  # cats()
  # solo()
  # edit_fields()