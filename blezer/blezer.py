import re
import csv
import requests
from bs4 import BeautifulSoup
from random import choice

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
  categories = soup.find('ul', id='menu-list').find_all('a')
  for category in categories[:-1]:
    cat_name = category.text
    cat_link = category.get('href') + '?limit=10000'
    get_products(cat_link)
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_products(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  products = soup.find_all('div' ,class_="product-layout")
  for i in products:
    product_link = i.find('div', class_="product-name-modules").a.get('href')
    get_product(product_link)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def get_product(url, *args, **kwargs):
  soup = BeautifulSoup(get_html(url), 'lxml')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  panel = soup.find('div', class_='panel panel-default panel-body')
  divs = panel.find_all('div')
  quicks = {}
  for div in divs:
    if div.get('class') and div.get('class')[0].split('-')[0] == 'quick':
      text = div.text.split(':')
      quicks.update({text[0].strip():text[1].strip()})
  articule = quicks.get('Артикул', '')
  name = panel.h1.text
  price_raw = panel.find('ul', class_='list-unstyled')
  try: price_new = price_raw.find('span', class_="price-new").text
  except: price_new = ''
  try: price_old = price_raw.find('span', class_="price-old").text
  except: price_old = ''
  try: action = price_raw.find('span', class_='you-save').text.split(' ')[-1].strip('()')
  except: action = ''
  try: price = price_raw.find('span', class_='price').text
  except: price = ''
  price = price_new or price
  img = []
  main_img = soup.find('a', class_='thumbnail img-responsive card-product').img.get('src')
  img.append(main_img)
  additional_imgs = soup.find_all('a', class_='img-thumbnail thumbnail')
  for i in additional_imgs:
    img.append(i.get('href'))
  manufacturer = quicks.get('Производитель', '')
  country = quicks.get('Страна', '')
  avaliable = quicks.get('Наличие', '')
  category = soup.find('ul', class_='breadcrumb').find_all('li')[1].a.text
  desc = soup.find('div', id='tab-description').text.strip()
  sizes_name = 'Размеры'
  sizes_measurment = 'см'
  sizes = []
  for radio in soup.find_all('div', class_='radio'):
    sizes.append(''.join(radio.text.replace(' ', '').split()))
  # sizes = set(sizes)
  # print(sizes)
  if sizes == []:
    sizes = quicks.get('Размеры', '')
  print(sizes)
  weight = quicks.get('Вес', '')
  extends = quicks.get('Расширение', '')
  material = quicks.get('Материал', '')
  table = soup.find('table', class_='table table-bordered')
  gender = ''
  colour = ''
  wheels = ''
  beauty = 'Нет'
  hand = 'Нет'
  try:
    text = table.text.split()
    if text.index('Кол-во'):
      wheels = text[text.index('Кол-во')+2]
    if text.index('Цвет'):
      colour = text[text.index('Цвет')+1]
      print(colour)
    beauty = 'Да' if 'Бьюти-кейс' in table.text else 'Нет'
    hand = 'Да' if 'Ручная кладь' in table.text else 'Нет'
    gender = ''
  except: pass
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  data = {
    # основные поля
    'articule':articule,
    'name':name,
    'searches':'',
    'desc':desc,
    'type':'r',
    'price':price.replace('р.',''),
    'price_from':'',
    'currency': 'RUB',
    'measurment_unit':"шт",
    'minimum':'', 'wholesale':'', 'minimums_wholesale':'', 'amount':'',     
    'img':[i for i in img],
    'avaliable':'+',#avaliable,      
    'action':action, 'action_from':'', 'action_to':'', 'label':'',
    'manufacturer':manufacturer,
    'country':country, 
    'HTML_header':'', 'HTML_description':'', 'HTML_keywords':'', 
    'gifts':'', 'group_number':'', 'group_name':'', 'subsection_address':'', 
    'delivery_possibility':'', 'delivery_terms':'', 'packing':'', 'personal_notes':'',
    'product_link':url,
    'GTIN':'', 'MPN':'',
    'product_id':articule,
    'product_unique_id':'', 'subsection_id':'',
    'group_id':category,
    'species_group_id':'',
    

    'sizes_name': sizes_name,           # Название_Характеристики   
    "sizes_measurment":sizes_measurment,# Измерение_Характеристики   
    'sizes':sizes,                      # Значение_Характеристики

    'weight_name': 'Вес',          
    "weight_measurment":'кг',  
    'weight':weight, 

    'extends_name': "Расширение",        
    "extends_measurment":"",  
    'extends':extends,  

    'material_name': "Материал",          
    "material_measurment":"",  
    'material':material, 

    # 'gender_name':'Пол',
    # 'gender_measurment':'',
    # 'gender':gender,

    'wheels_name':"Кол-во колес",
    'wheels_measurment':'',
    'wheels':wheels,
    
    'colour_name':'Цвет',
    'colour_measurment':'',
    'colour':colour,

    'beauty_name': 'Бьюти-кейс',
    'beauty_measurment': '',
    'beauty': beauty,

    'hand_name': 'Ручная кладь',
    'hand_measurment': '',
    'hand': hand,


  }
  global COUNTER; COUNTER += 1; print(COUNTER);
  print(name)
  print(url)
  write_csv(data)


def write_csv(data):
  with open('raw_blezer.csv', 'a') as f:
      # order = [
      #   'name', 'price', 'desc', 
      #   'cat', 'subcat', 'link', 
      #   'img_name', 'img_link'
      # ]
      order = list(data.keys())
      writer = csv.DictWriter(f, fieldnames=order)
      writer.writerow(data)


def edit_fields():
  raw_2 = open('raw_blezer2.csv', 'r')
  edited_raw_2 = open('edited_raw_blezer.csv', 'w')
  # for line in f:
  #   print(line)
  c = raw_2.read()
  c = c.replace("['","'")
  c = c.replace("']","'")
  c = c.replace('Чемоданы на колесиках', "9980")
  c = c.replace('Пластиковые чемоданы', "9981")
  c = c.replace('Дорожные саквояжи', "9982")
  c = c.replace('Детские чемоданы', "9983")
  c = c.replace('Детские игрушки', "9984")
  c = c.replace('Сумки на колесиках', "9985")
  c = c.replace('Чемоданы кейс-пилот', "9986")
  c = c.replace('Хозяйственные сумки тележки', "9987")
  c = c.replace('Рюкзаки', "9988")
  c = c.replace('Чехлы для чемоданов', "9989")
  c = c.replace('Детское постельное белье', "9990")
  c = c.replace('Постельное белье', "9991")
  c = c.replace('Сумки для ноутбука', "9992")
  c = c.replace('Комплекты чемоданов', "9993")
  c = c.replace('Мешки для обуви', "9994")
  c = c.replace('Рюкзаки школьные', "9995")
  c = c.replace('Уцененный товар', "9996")
  edited_raw_2.write(c)
  edited_raw_2.close()
  raw_2.close()



def cats():
  url2 = 'https://www.blezer.ru/chemodany_na_kolesikax/'+ '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/plastikovii_chemodan/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/index.php?route=product/category&path=79' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/detskie_chemodani/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/detskie_igrushki/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/symki_na_kolesikah/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/index.php?route=product/category&path=162' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/hozyaistvenie_symki/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/portfel/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/chekhly-dlya-chemodanov/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/detskoe-postelnoe-belie/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/postelnoe-belio/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/index.php?route=product/category&path=157' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/index.php?route=product/category&path=159' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/meshki_dlya_obuvi/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/shkolnye_ryukzaki/' + '?limit=10000'
  get_products(url2)
  url2 = 'https://www.blezer.ru/discounted/' + '?limit=10000'
  get_products(url2)

def solo():
  # url3 = 'https://www.blezer.ru/index.php?route=product/product&path=162&product_id=3351'
  # url3 = 'https://www.blezer.ru/index.php?route=product/product&path=67&product_id=1749'
  # url3 = 'https://www.blezer.ru/plastikovii_chemodan/1203.html'
  # url3 = 'https://www.blezer.ru/index.php?route=product/product&path=79&product_id=673'
  # url3 = 'https://www.blezer.ru/index.php?route=product/product&path=79&product_id=678'
  url3 = 'https://www.blezer.ru/index.php?route=product/product&path=63&product_id=2949'
  get_product(url3)

def main():
  get_categories('https://www.blezer.ru/')


if __name__ == '__main__':
  # main()
  # cats()
  # solo()
  edit_fields()