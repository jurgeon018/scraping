import requests
import csv
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from time import sleep
import json 


COUNTER = 0

class Parser(object):

  categories_filename = 'categories.csv'
  products_filename = 'products.csv'
  biggest_id = 9000
  categories = [
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

  def turbo(self, *args, **kwargs):
    '''Реализация многопоточности'''
    function = kwargs.get('function','')
    sequence = kwargs.get('sequence','')
    processes= kwargs.get('processes', 20)
    with Pool(processes) as pool:
      pool.map(function, sequence)

  def get_products_sheet(self, *args, **kwargs):
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

  def get_categories_sheet(self, *args, **kwargs):
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

  def write_category(self, *args, **kwargs):
    '''Записывает категории в csv-файл'''
    name      = kwargs.get('name', '')
    id        = kwargs.get('id', '')
    parent_id = kwargs.get('parent_id','')
    data      = self.get_categories_sheet()
    data['Название_группы']        = name
    data['Идентификатор_группы']   = id
    data['Идентификатор_родителя'] = parent_id
    self.write_csv(data, self.categories_filename)

  def write_categories(self, *args, **kwargs):
    '''Выбирает режим записи категорий в csv-файл'''
    turbo = kwargs.get('turbo', False)
    if turbo == True:
      self.turbo(function=self.write_category, sequence=self.categories)
    elif turbo == False:
      for category in self.categories:
        self.write_category(
          name=category['name'],
          id=category['id'],
          parent_id=category['parent_id'],
        )


  # ИЗМЕНЯЕМОЕ ВСПОМОГАТЕЛЬНОЕ:

  #  ПРОВЕРКА НА ТОВАРЫ\КАТЕГОРИИ
  def products_or_categories(self, url, *args, **kwargs):
    """Проверяет, находятся ли по ссылке категории товары,
    привязанные к этой категории, или подкатегории"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    products = soup.find_all('a', class_='products-view-name-link')
    categories = soup.find_all('a', class_='product-categories-header-slim-title')
    response = {}
    response['Products'] = False if products == [] else True
    response['Subcategories'] = False if categories == [] else True
    return response
  
  #  ТОВАРЫ ИЗ СПИСКА СТРАНИЦ
  def get_products_links(self, *args, **kwargs):
    ''' Из списка страниц парсит список товаров '''
    if kwargs.get('json',True):
      with open('pages_links.json','r') as file:
        links = json.load(file)['pages_links']
    if kwargs.get('variable', False):
      links = self.pages_links
    for url in links:
      self.get_products(url['url'])

  #  ИНФОРМАЦИЯ ПРО ТОВАР ИЗ СПИСКА СТРАНИЦ
  def get_products_from_links(self, *agrs, **kwargs):
    ''' Из списка товаров парсит информацию про товар'''
    if kwargs.get('json', True):
      with open('products_links.json','r') as file:
        links = json.load(file)['products_links']
    if kwargs.get('variable', False):
      links = self.products_links
    if kwargs.get('turbo',''):
      self.turbo(
        function=self.write_product_info, 
        sequence=[link['url'] for link in links], 
        processes=20
      )
    else:
      for link in links:
        self.write_product_info(link['url'])

  # ИЗМЕНЯЕМОЕ ОСНОВНОЕ:

  #  КАТЕГОРИИ
  def get_categories(self, url, *args, **kwargs):
    '''Достает ссылки всех категорий\субкатегорий при помощи рекурсии.
      Можно еще попробовать метод parent() на html-списках.'''
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    parent_name = kwargs.get('parent_name','')
    parent_id   = kwargs.get('parent_id', '')
    ############################################################################

    categories = soup.find_all('a', class_='product-categories-header-slim-title')
    for cat in categories:
      url  = cat.get('href')
      name = cat.text.strip()

    ############################################################################
      self.biggest_id += 1
      id = self.biggest_id
      category = {
        "id": id,
        "name":name,
        "parent_id":parent_id,
        "url":url,
      }
      print('category: ', category)
      self.categories.append(category)
      # self.write_json({'categories':self.categories}, 'categories.json', 'w')  

      # Код ниже можно писать тут, а можно писать write_categories() в main() после get_categories() либо в get_categories() после for
      # if kwargs.get('way_1', False) == True:
      #   self.write_category(name=name, id=id, parent_id=parent_id)

      if self.products_or_categories(url)['Subcategories'] == True:
        self.get_categories(url, parent_name=name, parent_id=id, parent_url=url)

      # Код ниже нужно закомментировать, если хочешь спарить ТОЛЬКО КАТЕГОРИИ, и не парсить товары.
      # Нужно для работы функции test_single()
      if self.products_or_categories(url)['Products'] == True:
        self.get_pages_links(url)

    # Код ниже можно писать тут, а можно писать в main() после get_categories()
    # if kwargs.get('way_2', False) == True:
    #   self.write_categories(turbo=False)

  #  ПАГИНАЦИЯ
  def get_pages_links(self, url, start=1, stop=None, step=1):
    ''' Создает список со страницами со списками товаров'''
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    ############################################################################

    category = soup.h1.text.strip()
    last_page = soup.find('div', class_="pagenumberer")
    if last_page == None:
      last_page = 1
    else:
      last_page = last_page.find_all('a')[-2].text.strip()
    page_pattern = '?page={i}'

    ############################################################################
    for i in range(1, int(last_page)+1):
      url = url.split('?')[0]+page_pattern.format(i=i)
      page = {
        "url":url,
        "category":category,
      }
      print('page: ', page)
      self.pages_links.append(page)
      # self.write_json({'pages_links':self.pages_links}, 'pages_links.json', 'w')  

      # !!! or 
      # self.get_products(url)
  
  #  ТОВАРЫ
  def get_products(self, url, *args, **kwargs):
    ''' Создает список со страницами товаров'''
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    ############################################################################

    # category = soup.h1.text.strip()
    products = soup.find_all('h4')#, class_='products-view-name-link')
    for product in products:
      link = product.a.get('href')

    ############################################################################
      product = {
        "url":link,
        # "category":category
      }
      print('product: ', product)
      self.products_links.append(product)
      self.write_json({'products_links':self.products_links}, 'products_links.json', 'w')  

      # !!! or 
      # self.write_product_info(url=link)

  #  ИНФОРМАЦИЯ ПРО ТОВАР
  def write_product_info(self, url, *args, **kwargs):
    """Достает информацию про товар и записывает ее в файл"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')  
    print(url)
    name         = self.get_name(soup)
    category     = self.get_category(soup)
    desc         = self.get_description(soup)
    imgs         = self.get_imgs(soup)
    articule     = self.get_articule(soup)
    price        = self.get_price(soup)[0]
    currency     = self.get_price(soup)[1]
    availability = self.get_availability(soup)
    data         = self.get_products_sheet()
    data         = self.get_features(soup, data)
    data['Код_товара']           = articule
    data['Название_позиции']     = name
    data['Описание']             = desc
    data['Тип_товара']           = 'r'
    data['Цена']                 = price
    data['Валюта']               = currency
    data['Единица_измерения']    = 'шт'
    data['Продукт_на_сайте']     = url
    data['Идентификатор_группы'] = category
    data['Идентификатор_товара']  = articule
    data['Ссылка_изображения']   = imgs
    data['Наличие']              = availability
    
    # print('\n') 
    # print("Ссылка: ",url)
    # print("Изображения: ", imgs)
    # print("Название: ",name)
    # print("Артикул: ",articule)
    # print("Цена: ",price)
    # print("Валюта: ",currency)
    # print("Категория: ",category)
    # print("Описание: ",desc)
    # print('\n')
    # print(data)
    self.write_csv(data=data, filename=self.products_filename)
  
  #  ПОЛЯ ТОВАРА
  def get_name(self, *args, **kwargs):
    soup = args[0]
    name  = soup.h1.text.strip()
    return name

  def get_category(self, *args, **kwargs):
    soup = args[0]
    category = soup.find('div', id="thumbs").find_all('span')[-2].text.strip()
    print(category)
    print(category == 'Фільтри для очищення питної води')
    if category == "Фільтри для очищення питної води":
      category = 9001 
    if category == "Змінні картриджі для води":
      category = 9002 
    if category == "Магістральні фільтри для води":
      category = 9003 
    if category == "Фільтраційні системи":
      category = 9004 
    if category == "Фільтри для побутової техніки":
      category = 9005 
    if category == "Змінні картриджі для води":
      category = 9007 
    if category == "Фільтруючі засипки для очищення води":
      category = 9008 
    if category == "Випромінювачі":
      category = 9009 
    if category == "Аксесуари":
      category = 9010 
    if category == "Басейни":
      category = 9012 
    if category == "Роботи пилососи для басейнів":
      category = 9013 
    if category == "Засоби догляду за басейном":
      category = 9014 
    if category == "Реагенти":
      category = 9016 
    if category == "Станції хімічної промивки мембран":
      category = 9017 
    if category == "Станції дозування":
      category = 9018 
    if category == "Диспенсери":
      category = 9020 
    if category == "Автомати":
      category = 9021 
    if category == "Кіоски":
      category = 9022 
    return category

    if self.categories:
      sequence = self.categories
    else:
      with open('categories.json','r') as file:
        sequence = json.load(file)['categories']
    for cat in sequence:
      if cat["name"] == category:
        return cat["id"]

  def get_description(self, *args, **kwargs):
    soup = args[0]
    desc = soup.find('section', id="description")
    return desc

  def get_imgs(self, *args, **kwargs):
    soup = args[0]
    imgs = []
    try:
      small_imgs  = soup.find('div', id='small-gallery').find_all('div', class_='item')
      for img in small_imgs:
        imgs.append(img.a.get('href'))
    except:
      pass
    big_img = soup.find('div', class_='big-image').a.get('href')
    imgs.append(big_img)
    return ', '.join(imgs)

  def get_articule(self, *args, **kwargs):
    soup = args[0]
    articule = soup.find('div', class_="code").text.split(' ')[-1].strip()
    with open(self.categories_filename, 'r') as file:
      if articule in file.read():
        articule += '__2'
    with open(self.categories_filename, 'r') as file:
      if articule in file.read():
        articule = articule[0:-3]+'__3'
    with open(self.categories_filename, 'r') as file:
      if articule in file.read():
        articule = articule[0:-3]+'__4'
    return articule

  def get_price(self, *args, **kwargs):
    soup = args[0]
    try:
      raw = soup.find('div', class_='actual').text.strip()
      if raw == None:
        raw = soup.find('div', class_='price-current')
      currency = raw.split(' ')[-1]
      price = ''.join(raw.split(' ')[0:-1])
    except Exception as e:
      print('get_price()')
      print(e)
      price = ''
      currency = ''
    return (price, currency.replace('грн','UAH'))

  def get_availability(self, *args, **kwargs):
    soup = args[0]
    try:
      availability = soup.find('span', class_='in-stock').text.strip()
    except:
      availability = soup.find('span', class_='available-d').text.strip()
    # print(availability == 'Нет в наличии / Возможность заказа уточняйте')
    if availability == 'Нет в наличии / Возможность заказа уточняйте':
      availability = '-'
    if availability == 'В наличии':
      availability = '+'
    return availability

  def get_features(self, *args, **kwargs):
    soup = args[0]
    data = args[1]
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


def main():
  parser = Parser()
  # Создает parser.categories, parser.pages_links и parser.products_links
  # parser.get_categories(url, way_1=False, way2=False)
  # Единажды - Запись списков с категориями, страницами, и товарами в json
  # parser.write_json({'categories':parser.categories}, 'categories.json')  
  # parser.write_json({'pages_links':parser.pages_links}, 'pages_links.json')  
  # parser.write_json({'products_links':parser.products_links}, 'products_links.json')  
  # Единажды - Запись категорий в csv
  # parser.write_categories(turbo=Fase) 
  # можно писать тут, а можно писать в get_categories() после for. 
  # Лучше тут, потому что парсить категории все равно надо будет только 1 раз

  # Создает products_links()
  # parser.get_products_links()
  # parser.get_products_from_links(turbo=True)  
  # Если хочешь парсить отсюда ^ (со списка ссылок), то в:
  # в get_pages_links()
  # в get_products()
  # после:
  #   !!! or
  # закоментируй:
  #   self.get_products(url)
  #   self.write_product_info(url=link)


  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/filtry/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/kartridzhi/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/magistralnye/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/filtracionnye-sistemy?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/filtry-dlya-bytovoy-tehniki/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/kartridzhi/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/zasypki/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/izluchateli/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/aksessuary/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/basseyny/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/roboty-pylesosy-dlya-basseynov/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/sredstva-uhoda-za-basseynom/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/reagenty/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/stancii-himicheskoy-promyvki-membran/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/stancii-dozirovaniya/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/dispensery/?limit=10000")
  # parser.get_products("https://ecosoft-market.com.ua/ua/shop/avtomaty/?limit=10000")

  parser.get_products_from_links(turbo=True)  



def test_single():
  parser = Parser()
  url = 'https://ecosoft-market.com.ua/ua/ecosoft/ecosoft-sense'
  parser.write_product_info(url)


if __name__ == '__main__':
  main()
  # test_single()