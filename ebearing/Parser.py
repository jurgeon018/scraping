import requests
import csv
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from time import sleep

COUNTER = 0

class Parser(object):
  categories = {}
  category_index = 9000

  # ОБЩИЕ

  def write_csv(self, data, filename):
    """Записывает информацию про товар в файл"""
    global COUNTER; COUNTER += 1; print(COUNTER)
    with open(filename, 'a') as file:
      # order = ['name', 'price', 'desc', 'cat', 'subcat', 'link', 'img_name', 'img_link']
      order = list(data.keys())
      writer = csv.DictWriter(file, fieldnames=order)
      writer.writerow(data)

  def get_proxies(self):
    """Возвращает список прокси-серверов"""
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

  def get_html(self, url, proxies=None, headers=None):
    """Возвращает html-код страницы"""
    if proxies:
      p = self.get_proxies()
      proxies = { p['schema']: p['address']  }
    if headers:
      headers = headers
    else:
      headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    r = requests.get(url, proxies=proxies, headers=headers)
    return r.content if r.ok else print('ERROR OCCURED. STATUS CODE:',r.status_code)
  
  def get_fieldnames(self, *args, **kwargs):
    """Возвращает список полей, нужных для шаблона прома"""
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

  # СПЕЦИАЛЬНЫЕ
  
  def get_categories(self, url, *args, **kwargs):
    '''Достает ссылки всех категорий(с главной страницы\страницы со списком всех категорий)'''
    soup = BeautifulSoup(get_html(url), 'lxml')
    links = soup.find('div', {'class':'sitemap-info'}).find('div', class_='left').find_all('a')
    for link in links[318:]:
      cat_name = link.text
      url = link.get('href')+'?limit=10000'
      try:get_products(url, cat_name)
      except Exception as e: print(e)    

  def pagination(self, url, start=1, stop=None, step=1, turbo=False):
    '''Достает ссылки всех страниц со списками товаров(с главной страницы\страницы категории)'''
    links = [f'{url}?p={str(i)}' for i in range(1, 809)]
    if turbo: 
      with Pool(20) as pool:
        pool.map(self.get_products, links)
    else:
      for link in links:
        # print(link)
        self.get_products(link)

  def get_products(self, url, *args, **kwargs):
    """Достает ссылки всех товаров(с главной страницы\страницы категории)"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    products = soup.find_all('li', class_='ajax_block_product col-xs-12 col-sm-6 col-md-4')
    for product in products:
      link = product.a.get('href')
      self.get_product(link)
      # print(link)

  def get_name(self, *args, **kwargs):
    soup = args[0]
    name = soup.find('h1').text
    return name

  def get_category(self, *args, **kwargs):
    soup = args[0]
    category = soup.find('div', class_='breadcrumb').find_all('span', itemprop="title")[-1].text.strip()
    if category == 'Подшипники с корпусом' or category == 'Підшипники з корпусом':
      category = '9014'
    if category == 'Подшипник' or category == 'Підшипник':
      category = '9000'
    if category == 'Шариковые' or category == 'Кулькові':
      category = '9001'
    if category == 'Однорядные радиальные' or category == 'Однорядні радіальні':
      category = '9002'
    if category == 'Двурядные радиальные' or category == 'Дворядні радіальні':
      category = '9003'
    if category == 'Радиально-упорные' or category == 'Радіально-упорні':
      category = '9004'
    if category == 'Упорные' or category == 'Упорні':
      category = '9005'
    if category == 'Роликовые' or category == 'Роликові':
      category = '9006'
    if category == 'Цилиндрические' or category == 'Циліндричні':
      category = '9007'
    if category == 'Игольчатые' or category == 'Голкові':
      category = '9008'
    if category == 'Сферические' or category == 'Сферичні':
      category = '9009'
    if category == 'Конические' or category == 'Конічні':
      category = '9010'
    if category == 'Корпусные узлы' or category == 'Корпусні вузли':
      category = '9011'
    if category == 'Фланцевый корпус' or category == 'Фланцевий корпус':
      category = '9012'
    if category == 'Закрепляемые' or category == 'Вставні':
      category = '9013'
    if category == 'Скольжения' or category == 'Ковзання':
      category = '9015'
    if category == 'Шарнирные головки' or category == 'Шарнірні головки':
      category = '9017'
    if category == 'Шарнирные' or category == 'Шарнірні':
      category = '9016'
    if category == 'Линейные' or category == 'Лінійні':
      category = '9018'
    if category == 'Втулки' or category == 'Втулки':
      category = '9019'
    if category == 'Агротехника и оборудование' or category == 'Агротехніка та обладнання':
      category = '9020' 
    return category
  
  def get_description(self, *args, **kwargs):
    soup = args[0]
    # desc = soup.find('div', class_='product-full-description')
    desc = soup.find('div', class_='product-full-description').text.strip()
    raw_desc = desc.replace('\n', ' ').split(' ')
    try: manufacturer = raw_desc[raw_desc.index('Производитель:')+1]
    except: manufacturer = ''
    try: country = raw_desc[raw_desc.index('происхождения:')+1]
    except: country = ''
    return (desc, manufacturer, country)
  
  def get_imgs(self, *args, **kwargs):
    soup = args[0]
    imgs = []
    try:
      lis = soup.find('ul', id='thumbs_list_frame').find_all('li')
      if lis:
        for li in lis:
          imgs.append(li.a.get('href'))
      elif not lis:
        img = soup.find('img', id='bigpic').get('src')
    except:
      img = ''
    return ', '.join(imgs)
  
  def get_articule(self, *args, **kwargs):
    soup = args[0]
    articule = soup.find('span', class_='product-code').find('span', class_='value').text
    return articule
  
  def get_price(self, *args, **kwargs):
    soup = args[0]
    raw_price = soup.find('span', class_='price product-price').text.strip().split(' ')
    price = ''.join(raw_price[0:-1]).replace(',','.')
    currency = raw_price[-1]
    return (price, currency)
  
  def get_availability(self, *args, **kwargs):
    soup = args[0]
    availability = soup.find('span', class_='availability').text.strip()
    if availability == '':
      availability = soup.find('span', class_='available-now').get('title')
    return availability

  def get_features(self, *args, **kwargs):
    soup = args[0]
    data = args[1]
    # bs = [i.text for i in soup.find_all('b')]
    # iss = [i.text for i in soup.find_all('i')]
    # # prod_params = list(zip(bs, iss))
    # prod_params = dict(zip(bs, iss))

    params = {}
    params_dict = {}
    try:
      trs = soup.find('div', class_='product-parameters').find_all('tr')
      for tr in trs:
        char = tr.th.text.strip().replace('\n', ' ')
        value = tr.td.text.strip().replace('\n', ' ')
        params.update({char:value})
    except Exception as e:
      print(e)
    for key, value in params.items():
      params_dict.update({
        f'Характеристика_{key}':key,
        f'Измерение_{key}'     :'',
        f'Значение{key}'       :value
      })
    data.update(params_dict)
    return data

  def get_product(self, url, *args, **kwargs):
    """Достает информацию про товар и записывает ее в файл"""
    soup = BeautifulSoup(self.get_html(url), 'lxml')   
    name         = self.get_name(soup)
    category     = self.get_category(soup)
    imgs         = self.get_imgs(soup)
    articule     = self.get_articule(soup)
    desc         = self.get_description(soup)[0]
    manufacturer = self.get_description(soup)[1]
    country      = self.get_description(soup)[2]
    price        = self.get_price(soup)[0]
    currency     = self.get_price(soup)[1]
    availability = self.get_availability(soup)

    data         = self.get_fieldnames()
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
    data['Наличие']              = '+'#availability
    data['Производитель']        = manufacturer
    data['Страна_производитель'] = country
    data         = self.get_features(soup, data)
    print('\n') 
    print("Ссылка: ",url)
    print("Изображения: ", imgs)
    print("Название: ",name)
    print("Артикул: ",articule)
    print("Цена: ",price)
    print("Валюта: ",currency)
    print("Категория: ",category)
    print("Наличие: ",availability)
    print("Производитель: ",manufacturer)
    print("Страна: ",country)
    print('\n')
    # category_index += 1
    # self.category[category] = category_index
    self.write_csv(data=data, filename='ebearing_ua.csv')

  def edit_categories(self):
    categories = open('categories.csv', 'r')
    edited_categories = open('edited_categories.csv', 'w')
    c = categories.read()
    # c = c.replace("['","'")
    # c = c.replace("']","'")
    c = c.replace('Подшипники с корпусом',     '9014')
    c = c.replace('Подшипник',	               '9000')
    c = c.replace('Шариковые',	               '9001')
    c = c.replace('Однорядные радиальные',     '9002')
    c = c.replace('Двурядные радиальные',      '9003')
    c = c.replace('Радиально-упорные',	       '9004')
    c = c.replace('Упорные',	                 '9005')
    c = c.replace('Роликовые',	               '9006')
    c = c.replace('Цилиндрические',	           '9007')
    c = c.replace('Игольчатые',	               '9008')
    c = c.replace('Сферические',         	     '9009')
    c = c.replace('Конические',	               '9010')
    c = c.replace('Корпусные узлы',	           '9011')
    c = c.replace('Фланцевый корпус',	         '9012')
    c = c.replace('Закрепляемые',	             '9013')
    c = c.replace('Скольжения',	               '9015')
    c = c.replace('Шарнирные головки',	       '9017')
    c = c.replace('Шарнирные',	               '9016')
    c = c.replace('Линейные',	                 '9018')
    c = c.replace('Втулки',	                   '9019')
    c = c.replace('Агротехника и оборудование','9020') 

    edited_categories.write(c)
    edited_categories.close()
    categories.close()



if __name__ == '__main__':

  parser = Parser()

  # parser.edit_categories()

  # url = 'https://ebearing.com.ua/ru/sitemap'
  # parser.get_categories(url)

  url = 'https://ebearing.com.ua/ru/catalog/cat-198-podshipnik'
  url = 'https://ebearing.com.ua/uk/catalog/cat-198-podshipnik'
  try:
    parser.pagination(url, stop=809, turbo=True)
  except: pass

  url = 'https://ebearing.com.ua/ru/catalog/cat-198-podshipnik?p=1'
  # parser.get_products(url)

  url1 = 'https://ebearing.com.ua/ru/khomuty/79337-khomut-plastikovyj-25kh150-belyj-100-sht.html' 
  # с 1 фоткой

  url2 = 'https://ebearing.com.ua/ru/odnoryadnye-radialnye/115586-1000081-681-s-681h-ezo-podshipnik-sharikovyj-nerzhavejka.html' 
  # без фоток 

  url3 = 'https://ebearing.com.ua/ru/konicheskie/73601-09081-09196-fersa-konicheskij-rolikopodshipnik.html' 
  # много параметров, производитель, страна, 2 описания, 3 фотки, в наличии

  url4 = 'https://ebearing.com.ua/ru/sharnirnye/75088-shsp50-ge50es-podshipnik-sharnirnyj.html'
  # Доступно: доступно для заказа

  url5 = 'https://ebearing.com.ua/ru/odnoryadnye-radialnye/102234-100-6000-ckh-podshipnik-sharikovyj.html'
  # Почему то не парсит наличие

  url6 = 'https://ebearing.com.ua/ru/konicheskie/93887-33013jr-koyo-konicheskij-rolikopodshipnik.html'
  # 4значная цифра 

  # parser.get_product(url6)











