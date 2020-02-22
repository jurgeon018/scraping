import requests
import csv
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from time import sleep
import json 
import xlsxwriter
import glob


COUNTER = 0

class Parser(object):

  categories_filename = 'categories.csv'
  products_filename   = 'products.csv'
  biggest_id          = 9000
  categories_links_json = 'categories_links.json'
  pages_links_json      = 'pages_links.json'
  products_links_json   = 'products_links.json'
  categories_links = [
    # {
    #   "number":"",
    #   "name":"",
    #   "id":"",
    #   "parent_id":"",
    #   "url":"",
    # },
  ]
  pages_links      = [
    # {
    #   "url":"",
    #   "category":"",
    # },
  ]
  products_links   = [
    # {
    #   "url":"",
    #   "category":"",
    # },
  ]


  # НЕИЗМЕНЯЕМОЕ(ОБЩЕЕ)

  def write_csv(self, data, filename, mode='a'):
    """Записывает информацию в csv-файл"""
    global COUNTER; COUNTER += 1; print(COUNTER)
    with open(filename, mode) as file:
      # order = ['name', 'price', 'desc', 'cat', 'subcat', 'link', 'img_name', 'img_link']
      order = list(data.keys())
      writer = csv.DictWriter(file, fieldnames=order)
      writer.writerow(data)

  def write_xlsx(self, data, filename, mode='a'):
    ''' Записывает информацию в эксель-таблицу '''
    pass

  def write_json(self, data, filename, mode='a'):
    ''' Записывает в json-файл '''
    with open(filename, mode) as file:
      json.dump(data, file, indent=4, ensure_ascii=False)

  def get_proxies(self):
    """Возвращает список прокси-серверов"""
    html = requests.get('https://free-proxy-list.net/').text.strip()
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

  def get_html(self, url, proxies=False, headers=None):
    """Возвращает html-код страницы"""
    if proxies:
      p = self.get_proxies()
      proxies = { p['schema']: p['address']  }
    if headers:
      headers = headers
    else:
      headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    r = requests.get(url, proxies=proxies, headers=headers)
    return r.content if r.ok else print('ATTENTION! ERROR OCCURED WHILE REQUESTING THE PAGE. STATUS CODE:',r.status_code)

  def get_products_sheet(self):
    """Возвращает список полей товаров, нужных для шаблона прома"""
    fieldnames = {
      'Код_товара':'',
      'Название_позиции':'',
      'Поисковые_запросы':'',
      'Описание':'',
      'Тип_товара':'',
      'Цена':'',
      'Цена от':'',
      'Ярлык':'',
      'HTML_заголовок':'',
      'HTML_описание':'',
      'HTML_ключевые_слова':'',
      'Валюта':'',
      'Скидка':'',
      'Cрок действия скидки от':'',
      'Cрок действия скидки до':'',
      'Единица_измерения':'',
      'Минимальный_объем_заказа':'',
      'Оптовая_цена':'',
      'Минимальный_заказ_опт':'',
      'Ссылка_изображения':'',
      'Наличие':'',
      'Количество':'',
      'Производитель':'',
      'Страна_производитель':'',
      'Номер_группы':'',
      'Адрес_подраздела':'',
      'Возможность_поставки':'',
      'Срок_поставки':'',
      'Способ_упаковки':'',
      'Личные_заметки':'',
      'Продукт_на_сайте':'',
      'Идентификатор_товара':'',
      'Уникальный_идентификатор':'',
      'Идентификатор_подраздела':'',
      'Идентификатор_группы':'',
      'Подарки':'',
      'Сопутствующие':'',
      'ID_группы_разновидностей':'',
      'Название_Характеристики':'',
      'Измерение_Характеристики':'',
      'Значение_Характеристики':'',
      'Название_Характеристики':'',
      'Измерение_Характеристики':'',
      'Значение_Характеристики':'',
    }
    return fieldnames

  def get_categories_sheet(self):
    """Возвращает список полей категорий, нужных для шаблона прома"""
    fieldnames = {
      'Номер_группы':'',
      'Название_группы':'',
      'Идентификатор_группы':'',
      'Номер_родителя':'',
      'Идентификатор_родителя':'',
      'HTML_заголовок_группы':'',
      'HTML_описание_группы':'',
      'HTML_ключевые_слова_группы':'',
    }
    return fieldnames



  def create_categories_json(self, url, *args, **kwargs):
    soup        = BeautifulSoup(self.get_html(url), 'lxml')
    categories  = soup.find('ul', class_='tree').find_all('a')
    cat    = soup.find('ul', class_='tree').find_all('a')[1]
    for cat in categories:

      try:
        raw         = cat.parent.parent.find_previous_sibling()
        parent_name = raw.text.strip()
        parent_url  = raw.get('href')
        with open('categories_links.json', 'r') as file:
          links     = json.load(file)['categories_links']
          for link in links:
            if link['name'].strip() == parent_name:
              parent_id = link['id']
      except Exception as e:
        print(e)
        parent_name = ''
        parent_url  = ''
        parent_id   = ''

      url  = cat.get('href')
      name = cat.text.strip()
      self.biggest_id += 1
      id = self.biggest_id
      category = {
        "id": id,
        "name":name,
        "url":url,
        "parent_name":parent_name,
        "parent_url":parent_url,
        "parent_id":parent_id,
      }
      # print('category: ', category)
      self.categories_links.append(category)
    self.write_json({'categories_links':self.categories_links}, 'categories_links.json', 'w')  

  def create_pages_json(self, url, start=1, stop=None, step=1):
    soup      = BeautifulSoup(self.get_html(url), 'lxml')
    category  = soup.find('div', class_="breadcrumb").text.split('>')[-1].strip()#.text.strip()
    try:
      last_page = soup.find('ul', class_='pagination').find_all('li')[-2].text
    except:
      last_page = 1
    page_pattern = '?p={i}'
    for i in range(1, int(last_page)+1):
      url  = url.split('?')[0]+page_pattern.format(i=i)
      with open('categories_links.json', 'r') as file:
        links = json.load(file)['categories_links']
        for link in links:
          if link['name'].strip() == category.strip():
            id = link['id']
      page = {
        "url":url,
        "category":category,
        "id":id,
      }
      print('page: ', page)
      self.pages_links.append(page)
    self.write_json({'pages_links':self.pages_links}, 'pages_links.json', 'w')  

  def create_products_links(self, link):
    url = link['url']
    category = link['category']
    id = link['id']
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    if soup.find('div', id='subcategories') != None:
      return 
    products = soup.find_all('a', class_='product_img_link')
    for product in products:
      link = product.get('href')
      product = {
        "url":link,
        "category":category,
        "id":id,
      }
      print('product: ', product)
      self.products_links.append(product)
    self.write_json({'products_links':self.products_links}, 'products_links.json', 'w')  




  def write_product_info(self, data):
    """Достает информацию про товар и записывает ее в файл"""
    url      = data.get('url', '')
    category = data.get('category', '')
    id       = data.get('id','')
    soup = BeautifulSoup(self.get_html(url), 'lxml')  
    name         = self.get_name(soup)
    desc         = self.get_description(soup)
    imgs         = self.get_imgs(soup)
    articule     = self.get_articule(soup, url)
    price        = self.get_price(soup)[0]
    currency     = self.get_price(soup)[1]
    availability = self.get_availability(soup)
    # category     = self.get_category(category)
    category     = id
    data         = self.get_products_sheet()
    # data         = self.get_features(soup, data)
    data['Код_товара']           = articule
    data['Название_позиции']     = name
    data['Описание']             = desc
    data['Тип_товара']           = 'r'
    data['Цена']                 = price
    data['Валюта']               = currency
    data['Единица_измерения']    = 'шт'
    data['Продукт_на_сайте']     = url
    data['Идентификатор_группы'] = category
    data['Идентификатор_товара'] = articule
    data['Ссылка_изображения']   = imgs
    data['Наличие']              = availability
    print("Ссылка: ",     url     )
    print("Изображения: ",imgs    )
    print("Название: ",   name    )
    print("Артикул: ",    articule)
    print("Цена: ",       price   )
    print("Валюта: ",     currency)
    print("Категория: ",  category)
    print("Описание: ",   desc    )
    # print(data)
    self.write_csv(data=data, filename=self.products_filename)
  
  def get_name(self, soup):
    name  = soup.h1.text.strip()
    return name

  def get_category(self, category):
    # category = soup.find('ul', {'class':'breadcrumb'}).find_all('a')[-2].text.strip()
    try:
      with open('categories_links.json','r') as file:
        for json_category in json.load(file)['categories_links']:
          if json_category["name"].strip() == category.strip():
            return json_category["id"]
    except Exception as e:
      print(e)
    return category
    
    
  def get_description(self, soup):
    desc = soup.find('section', class_="page-product-box")
    return desc

  def get_imgs(self, soup):
    try:
      imgs = []
      thumbs = soup.find('ul', id="thumbs_list_frame").find_all('a', class_='fancybox')
      for img in thumbs:
        imgs.append(img.get('href'))
    except Exception as e:
      print('ERROR:',e)
      img = ''
    return ', '.join(imgs)

  def get_articule(self, soup, *args):
    articule = args[0].split('/')[-1].split('-')[0]
    return articule

  def get_price(self, soup):
    price = soup.find('span', id="our_price_display").text.split(' ')[0].strip().replace(',','.')
    currency = 'UAH'
    return (price, currency)

  def get_availability(self, soup):
    # availability = soup.find_all('ul', class_='list-unstyled')[1].find_all('li')[-1].text.strip()
    # if availability == 'Доступность: В наличии':
    #   availability = '+'
    # else:
    #   availability = '-'
    # return availability
    return '+'

  def get_features(self, soup, data):
    all_tds = []
    try:
      tbodys = soup.find('section', id="characteristics").find_all('tbody')
      for tbody in tbodys:
        tds = tbody.find_all('td')
        for td in tds:
          all_tds.append(td.text.strip())
      names = [td for td in all_tds if all_tds.index(td) % 2 == 0]
      values = [td for td in all_tds if all_tds.index(td) % 2 != 0]
      features = dict(zip(names, values))
      params_dict = {}
      for key, value in features.items():
        params_dict.update({
          f'Характеристика({key})':key,
          f'Измерение({key})'     :'',
          f'Значение({key})'      :value
        })
      data.update(params_dict)
    except Exception as e:
      print('get_features()')
      print(e)
    return data


def parse_categories():
  parser = Parser()
  url = 'http://gvardeisky.com.ua/343-poncho-nakidka-dozhdevik-olive-germaniya.html'
  parser.create_categories_json(url)


def write_categories():
  parser = Parser()
  with open('categories_links.json') as json_file:
    cats = json.load(json_file)['categories_links']
  with open('categories.csv', 'w') as csv_file:
    writer = csv.DictWriter(
      csv_file, 
      fieldnames=[k for k in parser.get_categories_sheet().keys()]
    )
    writer.writeheader()
  with open('categories.csv', 'a') as csv_file:
    for cat in cats:
      name      = cat['name']
      id        = cat['id']
      parent_id = cat.get('parent_id', '')
      data      = parser.get_categories_sheet()
      data['Название_группы']        = name
      data['Идентификатор_группы']   = id
      data['Идентификатор_родителя'] = parent_id
      parser.write_csv(data, 'categories.csv')


def parse_pages():
  parser = Parser()
  with open('categories_links.json') as file:
    for category in json.load(file)['categories_links']:
      url = category['url'] + '?page=1'
      parser.create_pages_json(url)


def parse_products_links():
  parser = Parser()
  with open('pages_links.json','r') as file:
    for link in json.load(file)['pages_links']:
      parser.create_products_links(link)


def write_products(turbo=False):
  parser = Parser()
  fieldnames = [k for k,v in parser.get_products_sheet().items()]
  with open('products.csv', 'w') as file:
    writer = csv.DictWriter(
      file, fieldnames=fieldnames
    )
    writer.writeheader()
  with open('products_links.json', 'r') as file:
    products = json.load(file)['products_links']
  if not turbo:
    for product in products:
      parser.write_product_info(product)
  else:
    with Pool(20) as pool:
      pool.map(
        parser.write_product_info, 
        [product for product in products]
      )


def create_xlsx():
  workbook          = xlsxwriter.Workbook('result.xlsx') 
  products_sheet    = workbook.add_worksheet('Export Products Sheet')
  categories_sheet       = workbook.add_worksheet('Export Group Sheet')
  products_reader   = csv.reader(open('products.csv', 'r'), delimiter=',',quotechar='"')
  categories_reader = csv.reader(open('categories.csv', 'r'), delimiter=',',quotechar='"')
  
  row_count = 0
  for row in products_reader:
    for col in range(len(row)):
      # products_sheet.write(row_count,col,row[col])
      products_sheet.write_string(row_count,col,row[col])
    row_count +=1

  row_count = 0
  for row in categories_reader:
    for col in range(len(row)):
      # categories_sheet.write(row_count,col,row[col])
      categories_sheet.write_string(row_count,col,row[col])
    row_count +=1
  
  workbook.close()


def test_pagination():
  parser = Parser()
  url = 'http://gvardeisky.com.ua/3-odezhda?p=1'
  url = 'http://gvardeisky.com.ua/19-obuv?p=1'
  url = 'http://gvardeisky.com.ua/17-kozhgalantereya?p=1'
  url = 'http://gvardeisky.com.ua/34-pokhodnye-aksesuary?p=1'
  url = 'http://gvardeisky.com.ua/58-prochee?p=1'
  url = 'http://gvardeisky.com.ua/59-rasprodazha?p=1'
  url = 'http://gvardeisky.com.ua/72-poncho?p=1'
  parser.create_pages_json(url)


def test_single_product():
  parser = Parser()
  data = {
    "url":'http://gvardeisky.com.ua/309-passivnye-strelkovye-naushniki-peltor-h61fa.html'
  }
  parser.write_product_info(data)


#1
# parse_categories() 
#2
# write_categories()
#3
# parse_pages() 
#4
# parse_products_links()
#5
# write_products(turbo=True)
#6
create_xlsx()



# test_single_product()
# test_pagination()