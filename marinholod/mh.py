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
  products = soup.find_all('div', class_='proddesc')
  products = soup.find_all('div', class_='prodimage')
  products = soup.find_all('div', class_='prodprice')
  for product in products:
    link = product.a.get('href')
    get_product(link)
    # print(link)
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_product(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  bs = [i.text for i in soup.find_all('b')]
  iss = [i.text for i in soup.find_all('i')]
  # prod_params = list(zip(bs, iss))
  prod_params = dict(zip(bs, iss))

  params = {}
  try:
    trs = soup.find('div', {"id":'params', 'class':'fullstorytab'}).find_all('tr')
    for tr in trs:
      char = tr.find_all('td')[0].text
      value = tr.find_all('td')[1].text
      params.update({char:value})
  except Exception as e:
    print(e)
  category = soup.find('span', id="dle-speedbar").find_all('a')[-1].text

  name  = params.get('Наименование', '')
  if name:
    name = name
  else:
    name = soup.h1.text
  

  try: desc = soup.find('div', class_='catalog_fulldesc')
  except: desc = ''

  try: img = soup.find('div', id="mnimage").a.get('href')
  except: img = ''
  
  articule = prod_params.get('Код завода', "")
  if articule == '':
    try: articule = soup.find_all('tr')[1].find_all('td')[0].text
    except Exception as e: print(e)

  price = prod_params.get('Рекомендованная розничная цена с НДС', "")
  # try:price = float(''.join([i for i in price if i not in ' ,р.'])) * 0.46
  try:price = int(float(price.split(',')[0].replace(' ', '')) * 0.46)
  except: price = ''


  print('url: ', url)
  print('img: ', img)
  print('name: ', name)
  print('category: ', category)
  print('prod_params: ', prod_params)
  print('params: ', params)
  print('articule: ', articule)
  print('price: ', price)
  print('\n')
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  data = {
    # основные поля
    'articule':articule,
    'name':name,
    'price':price,
    'currency': 'UAH',
    'measurment_unit':"шт",
    'type':'r',
    'avaliable':'+',    
    'group_id':category,
    'product_link':url,
    'img':img,л
    'desc':desc,

    # Название_Характеристики   
    # Измерение_Характеристики   
    # Значение_Характеристики


  }
  params_dict = {}
  for key, value in params.items():
    params_dict.update({key+'char':key,key+'measurment':'',key+'value':value})
  data.update(params_dict)

  # prod_params_dict = {}
  # for key, value in prod_params.items():
  #   prod_params_dict.update({key+'name':key,key+'measurment':'',key+'value':value})
  # data.update(prod_params_dict)


  write_csv(data)


def write_csv(data):
  global COUNTER; COUNTER += 1; print(COUNTER)
  with open('raw_mh.csv', 'a') as f:
      # order = [
      #   'name', 'price', 'desc', 
      #   'cat', 'subcat', 'link', 
      #   'img_name', 'img_link'
      # ]
      order = list(data.keys())
      writer = csv.DictWriter(f, fieldnames=order)
      writer.writerow(data)


def cats():
  for i in range(1, 34):
    url = f'http://www.mariholod.com/catalog-new/page/{i}/'
    get_products(url)
  

if __name__ == '__main__':
  url = 'http://www.mariholod.com/catalog-new/hv/489-holodilnaya-vitrina-vhn-18-ilet-new.html'
  # get_product(url)
  cats()