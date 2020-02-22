import requests
import csv
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from time import sleep
import xlsxwriter

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
    """Записывает информацию про товар в файл"""
    global COUNTER; COUNTER += 1; print(COUNTER)
    with open(filename, mode) as file:
      # order = ['name', 'price', 'desc', 'cat', 'subcat', 'link', 'img_name', 'img_link']
      order = list(data.keys())
      writer = csv.DictWriter(file, fieldnames=order)
      writer.writerow(data)

  def write_xlsx(self, data, filename, mode='a'):
    pass

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
    name      = kwargs.get('name', '')
    id        = kwargs.get('id', '')
    parent_id = kwargs.get('parent_id','')
    data      = self.get_categories_sheet()
    data['Название_группы']        = name
    data['Идентификатор_группы']   = id
    data['Идентификатор_родителя'] = parent_id
    self.write_csv(data, self.categories_filename)

  def write_categories(self, *args, **kwargs):
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
    """Проверяет, находятся ли по ссылке категории товары привязанные к этой категории, или там находятся подкатегории"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    products = soup.find_all('a', class_='products-view-name-link')
    categories = soup.find_all('a', class_='product-categories-header-slim-title')
    response = {}
    response['Products'] = False if products == [] else True
    response['Subcategories'] = False if categories == [] else True
    return response
  
  #  ТОВАРЫ ИЗ СПИСКА СТРАНИЦ
  def get_products_links(self, *args, **kwargs):
    for url in self.pages_links:
      get_products(url['url'])
  
  #  ИНФОРМАЦИЯ ПРО ТОВАР ИЗ СПИСКА СТРАНИЦ
  def get_products_from_links(self, *agrs, **kwagrs):
    if kwargs['turbo']:
      turbo(
        function=write_product_info, 
        sequence=[link['url'] for link in self.products_links], 
        processes=20
      )
    else:
      for link in self.products_links:
        write_product_info(link['url'])


  # ИЗМЕНЯЕМОЕ ОСНОВНОЕ:

  #  КАТЕГОРИИ
  def get_categories(self, url, *args, **kwargs):
    '''Достает ссылки всех категорий\субкатегорий при помощи рекурсии. Можно еще попробовать метод parent() на html-списках.'''
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    parent_name = kwargs.get('parent_name','')
    parent_id   = kwargs.get('parent_id', '')
    ############################################################################

    links = soup.find('div', {'class':'sitemap-info'}).find('div', class_='left').find_all('a')
    for link in links:
      cat_name = link.text
      url = link.get('href')+'?limit=10000'
      try:get_products(url, cat_name)
      except Exception as e: print(e)    

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

      # Код ниже можно писать тут, а можно писать write_categories() в main() после get_categories() либо в get_categories() после for
      # if kwargs.get('way_1', False) == True:
      #   self.write_category(name=name, id=id, parent_id=parent_id)

      if self.products_or_categories(url)['Subcategories'] == True:
        self.get_categories(url, parent_name=name, parent_id=id, parent_url=url)

      if self.products_or_categories(url)['Products'] == True:
        self.get_pages_links(url)
    # Код ниже можно писать тут, а можно писать в main() после get_categories()
    # if kwargs.get('way_2', False) == True:
    #   self.write_categories(turbo=False)

  #  ПАГИНАЦИЯ
  def get_pages_links(self, url, start=1, stop=None, step=1):
    '''Достает ссылки всех стран  иц со списками товаров(с главной страницы\страницы категории)'''
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    ############################################################################

    category = soup.h1.text.strip()
    last_page = soup.find('div', class_="pagenumberer")
    if last_page == None:
      last_page = 1
    else:
      last_page = last_page.find_all('a')[-2].text.strip()
    # page_pattern = '?page={i}'
    page_pattern = ''

    ############################################################################
    for i in range(1, int(last_page)+1):
      url = url+page_pattern.format(i=i)
      page = {
        "url":url,
        "category":category,
      }
      print('page: ', page)
      self.pages_links.append(page)
      # !!! or 
      self.get_products(url)
  
  #  ТОВАРЫ
  def get_products(self, url, *args, **kwargs):
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    ############################################################################


    category = args[0]
    products = soup.find_all('div', class_='img_cnt')
    for product in products:
      link = product.a.get('href')

    ############################################################################
      product = {
        "url":link,
        "category":category
      }
      # print('product: ', product)
      self.products_links.append(product)
      # !!! or 
      self.write_product_info(link, category)

  #  ИНФОРМАЦИЯ ПРО ТОВАР
  def write_product_info(self, url, *args, **kwargs):
    """Достает информацию про товар и записывает ее в файл"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')   
    name         = self.get_name(soup)
    category     = self.get_category(args[0])
    desc         = self.get_description(soup)
    imgs         = self.get_imgs(soup)
    # articule     = self.get_articule(soup)
    price        = self.get_price(soup)[0]
    currency     = self.get_price(soup)[1]
    # availability = self.get_availability(soup)
    manufacturer = self.get_manufacturer(soup)
    data         = self.get_products_sheet()
    data         = self.get_features(soup, data)
    # data['Код_товара']           = articule
    data['Название_позиции']     = name
    data['Описание']             = desc
    data['Тип_товара']           = 'r'
    data['Цена']                 = price
    data['Валюта']               = currency
    data['Единица_измерения']    = 'шт'
    data['Продукт_на_сайте']     = url
    data['Идентификатор_группы'] = category
    # data['Идентификтор_товара']  = articule
    data['Ссылка_изображения']   = imgs
    data['Наличие']              = '+'#availability
    data['Производитель']        = manufacturer
    
    print('\n') 
    print("Ссылка: ",url)
    # print("Изображения: ", imgs)
    # print("Название: ",name)
    # print("Артикул: ",articule)
    # print("Цена: ",price)
    # print("Валюта: ",currency)
    # print("Категория: ",category)
    print('Производитель:', manufacturer)
    # print("Описание: ",desc)
    print('\n')
    self.write_csv(data=data, filename=self.products_filename)
  
  #  ПОЛЯ ТОВАРА
  def get_name(self, soup, *args, **kwargs):
    name  = soup.h1.text.strip()
    return name

  def get_category(self, *args, **kwargs):
    category = args[0]
    if category == 'Каминные топки':	
      category = "'534124"
    if category == 'Печи':	
      category = "'499054"
    return category

  def get_description(self, *args, **kwargs):
    soup = args[0]
    ps = soup.find('div', class_='characteristics-block my-corner').find_all('p')
    desc = ''
    for p in ps:
      desc += p.text.strip().replace('\n\n\n', '\n').strip()
    return desc

  def get_imgs(self, *args, **kwargs):
    soup = args[0]
    img = []
    big_img = soup.find('a', id='big_imgg').get('href')
    img.append(big_img)
    for i in soup.find_all('a', class_='small-img'):
      img.append(i.get('href'))
    # img = [i for i in img]
    img = ', '.join(img)
    return img

  def get_articule(self, *args, **kwargs):
    soup = args[0]
    product = soup.find('div', class_='product-info')
    articule = soup.find('div', class_='details-param-value inplace-offset').text.strip()
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

  def get_price(self, soup, *args, **kwargs):
    raw_price = soup.find('span', class_='main-price').text.strip().split(' ')
    price = raw_price[0]
    currency = raw_price[1]
    return price, currency

  def get_availability(self, *args, **kwargs):
    soup = args[0]

    availability = soup.find('div', class_='availability').text.strip()
    if availability == 'Нет в наличии / Возможность заказа уточняйте':
      availability = '-'
    if availability == 'Есть в наличии / Возможно заказать':
      availability = '+'
    return availability

  def get_features(self, *args, **kwargs):
    soup   = args[0]
    data   = args[1]
    try:
      trs    = soup.find('div', class_='characteristics-block my-corner').find_all('tr')
      names  = [tr.find_all('td')[0].text.strip() for tr in trs]
      values = [tr.find_all('td')[1].text.strip() for tr in trs]
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
      print(e)
    return data

  def get_manufacturer(self, *args, **kwargs):
    soup = args[0]
    # manufacturer = soup.find('div', {'class':'product-main-block'}).find_all('section')[1].find_all('li')[1].span.text.strip()
    manufacturer = soup.find('div', {'class':'product-main-block'}).find_all('section')[1].find_all('span')[0].text.strip()
    return manufacturer

def main():
  parser = Parser()
  # url = 'https://shop220.com.ua/catalog'
  # parser.get_categories(url, way_1=False, way2=False)
  # parser.write_categories(turbo=Fase) 
  # # можно писать тут, а можно писать в get_categories() после for. 
  # # Лучше тут, потому что парсить категории все равно надо будет только 1 раз


  # # parser.get_pages_links()
  # # parser.get_products_links()
  # # parser.get_products_from_links(turbo=True)  
  # # Если хочешь парсить отсюда ^ (со списка ссылок), то в:
  # # в get_pages_links()
  # # в get_products()
  # # после:
  # #   !!! or
  # # закоментируй:
  # #   self.get_products(url)
  # #   self.write_product_info(url=link)

  
  # url = ['https://kaminlux.com.ua/goods.php/Stalnye-topki/Kaminnaya-topka-Hajduk-Volcano-2LTh/', 'Каминные топки','Стальные топки']
  # parser.write_product_info(url[0], url[1])
  # return
  url1 = ['https://kaminlux.com.ua/goods.php/Stalnye-topki/', 'Каминные топки', 'Стальные топки']
  url2 = ['https://kaminlux.com.ua/goods.php/CHugunnye-topki/', 'Каминные топки', 'Чугунные топки']
  url3 = ['https://kaminlux.com.ua/goods.php/Topki-s-vodyanym-konturom/', 'Каминные топки', 'Топки с водяным контуром']
  # Печи
  url4 = ['https://kaminlux.com.ua/goods.php/Otopitelnye-pechi/', 'Печи', 'Чугунные печи']
  url5 = ['https://kaminlux.com.ua/goods.php/Pechi-s-vodyanym-konturom/', 'Печи', 'Печи с водяным контуром']
  url6 = ['https://kaminlux.com.ua/goods.php/Stalnye-pechi/', 'Печи', 'Стальные печи']
  parser.get_products(url1[0], url1[1])
  parser.get_products(url2[0], url2[1])
  parser.get_products(url3[0], url3[1])
  parser.get_products(url4[0], url4[1])
  parser.get_products(url5[0], url5[1])
  parser.get_products(url6[0], url6[1])


if __name__ == '__main__':
  main()