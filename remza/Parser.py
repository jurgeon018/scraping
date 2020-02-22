import requests
import csv
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from time import sleep
import xlsxwriter
from categories import categories


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
    soup = BeautifulSoup(self.get_html(url), 'lxml')
    links = soup.find('div', {'class':'sitemap-info'}).find('div', class_='left').find_all('a')
    for link in links:#[79:80]:
      if link.get('href') in [
        'http://remza.com.ua/zaphasti_boilerov', 
        'http://remza.com.ua/zapchasti_dlja_gazovykh_kotlov_kolonok',
        'http://remza.com.ua/zapchasti_gaz_olit_i_duhovok',
        'http://remza.com.ua/melko_byt',
        'http://remza.com.ua/zapchasti_dlja_stiralnykh_mashin',
        'http://remza.com.ua/zapchasti_dlya_holod',
      ]: continue
      cat_name = link.text.strip()
      url = link.get('href')+'?limit=10000'
      try:self.get_products(url, cat_name, link.get('href'))
      except Exception as e: print('ddd',e)   

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
    cat_name = args[0]
    link = args[1]
    products = soup.find('div', class_="product-list").find_all('div', class_='name')
    for product in products:
      try:
        small_img = product.parent.find('div', class_="image").img.get('src')
      except:
        small_img = ''
      link = product.a.get('href')
      self.get_product(link, cat_name, link, small_img)

  def get_name(self, *args, **kwargs):
    soup = args[0]
    name  = soup.find('div', id="content").h1.text
    return name

  def get_category(self, *args, **kwargs):
    category = args[0].strip()
    if category == 'Запчасти для бойлеров':	
      category = '9000'
    if category == 'Аноды':	
      category = '9001'
    if category == 'Клавиша включения':	
      category = '9002'
    if category == 'Лампа сигнальная':	
      category = '9003'
    if category == 'Предохранительные клапана':	
      category = '9004'
    if category == 'Прокладки':	
      category = '9005'
    if category == 'Термостаты':	
      category = '9006'
    if category == 'Тэны':
      pattern = '/'.join(args[1].strip().split('/')[0:-1])
      if args[1].strip() == 'http://remza.com.ua/zaphasti_boilerov/ten_boilera':
        category = '9007'
      if pattern == 'http://remza.com.ua/zapchasti_gaz_olit_i_duhovok/nen_dyxovok':
        category = '9079'
    if category == 'Фланцы для бойлеров (водонагревателей)':	
      category = '9008'
    if category == 'Электронный модуль':	
      category = '9009'
    if category == 'Запчасти для газовых котлов и колонок':	
      category = '9010'
    if category == 'Аксессуары, оборудование и специнструмент':	
      category = '9011'
    if category == 'Вентиляторы, трубки Вентури, Пито': 
      category = '9012'
    if category == 'Газогорелочные устройства': 
      category = '9013'
    if category == 'Гидравлические комплектующие': 
      category = '9014'
    if category == 'Датчики NTC': 
      category = '9015'
    if category == 'Датчики протока, расходомеры': 
      category = '9016'
    if category == 'Клапана безопасности и воздушные клапана': 
      category = '9017'
    if category == 'Краны подпитки': 
      category = '9018'
    if category == 'Манометры, термометры и термоманометры': 
      category = '9019'
    if category == 'Мембраны (диафрагмы)': 
      category = '9020'
    if category == 'Пилотные (запальные) горелки': 
      category = '9021'
    if category == 'Платы управления и розжига': 
      category = '9022'
    if category == 'Прессостаты для газовых котлов': 
      category = '9023'
    if category == 'Расширительные баки': 
      category = '9024'
    if category == 'Реле давления воды': 
      category = '9025'
    if category == 'Теплообменники': 
      category = '9026'
    if category == 'Термопары': 
      category = '9027'
    if category == 'Терморегуляторы (программаторы, термостаты)': 
      category = '9028'
    if category == 'Термостаты': 
      category = '9029'
    if category == 'Трансформаторы розжига': 
      category = '9030'
    if category == 'Циркуляционные насосы': 
      category = '9031'
    if category == 'Электроды розжига и ионизации': 
      category = '9032'
    if category == 'Электромагниты, электромагнитные и газовые клапана': 
      category = '9033'
    if category == 'Электронные блоки розжига и управления': 
      category = '9034'
    if category == 'Запчасти для газовых плит и духовок': 
      category = '9035'
    if category == 'Вентиляторы': 
      category = '9036'
    if category == 'Газовые краны': 
      category = '9037'
    if category == 'Генераторы искры': 
      category = '9038'
    if category == 'Горелка - рассекатель': 
      category = '9039'
    if category == 'Горелки - рассекатели Nord 2002-2011': 
      category = '9040'
    if category == 'Горелки - рассекатели Nord, Greta новый 2012': 
      category = '9041'
    if category == 'Горелки - рассекатели Брест': 
      category = '9042'
    if category == 'Горелки - рассекатели Гефест': 
      category = '9043'
    if category == 'Горелки - рассекатели Гретта 2008-2011': 
      category = '9044'
    if category == 'Горелки - рассекатели Дружковка 2004-2008': 
      category = '9045'
    if category == 'Горелки - рассекатели Дружковка на длинной ножке': 
      category = '9046'
    if category == 'Горелки - рассекатели Дружковка на короткой ножке': 
      category = '9047'
    if category == 'Горелки - рассекатели с крышкой Дружковка старого образца': 
      category = '9048'
    if category == 'Горелки - рассекатели Электа': 
      category = '9049'
    if category == 'Горелки духовок': 
      category = '9050'
    if category == 'Жиклеры и сопла для плит': 
      category = '9051'
    if category == 'Кнопки генератора искры': 
      category = '9052'
    if category == 'Корпус рассекателя': 
      category = '9053'
    if category == 'Корпуса рассекателей Greta 2008-2011': 
      category = '9054'
    if category == 'Корпуса рассекателей Nord': 
      category = '9055'
    if category == 'Корпуса рассекателей Nord, Greta (новый)': 
      category = '9056'
    if category == 'Корпуса рассекателей Дружковка 2004-2008': 
      category = '9057'
    if category == 'Кронштейны для плит': 
      category = '9058'
    if category == 'Крышки горелки': 
      category = '9059'
    if category == 'Крышки горелок Electrolux': 
      category = '9060'
    if category == 'Крышки горелок Indesit': 
      category = '9061'
    if category == 'Крышки горелок Гефест': 
      category = '9062'
    if category == 'Крышки горелок Дружковка (внутренние)': 
      category = '9063'
    if category == 'Крышки горелок Дружковка (наружные)': 
      category = '9064'
    if category == 'Крышки горелок Норд, Грета, Дружковка': 
      category = '9065'
    if category == 'Крышки горелок Электа': 
      category = '9066'
    if category == 'Лампочки': 
      category = '9067'
    if category == 'Переключатели мощности': 
      category = '9068'
    if category == 'Прокладки для газового крана': 
      category = '9069'
    if category == 'Расходные материалы для газовых плит и духовок': 
      category = '9070'
    if category == 'Ручки': 
      category = '9071'
    if category == 'Свечи электроподжига': 
      category = '9072'
    if category == 'Стекла': 
      category = '9073'
    if category == 'Таймеры': 
      category = '9074'
    if category == 'Термометры': 
      category = '9075'
    if category == 'Термопары': 
      category = '9076'
    if category == 'Терморегуляторы (термостаты)': 
      category = '9077'
    if category == 'Трубки': 
      category = '9078'
    if category == 'Уплотнители': 
      category = '9080'
    if category == 'Электромагниты': 
      category = '9081'
    if category == 'Запчасти для мелкобытовой техники': 
      category = '9082'
    if category == 'Запчасти для блендеров': 
      category = '9083'
    if category == 'Запчасти для кухонных комбайнов': 
      category = '9084'
    if category == 'Запчасти для мясорубок': 
      category = '9085'
    if category == 'Аксессуары': 
      category = '9086'
    if category == 'Втулки': 
      category = '9087'
    if category == 'Корпус шнека (тубус)': 
      category = '9088'
    if category == 'Муфты сцепления (предохранители)': 
      category = '9089'
    if category == 'Насадки': 
      category = '9090'
    if category == 'Ножи': 
      category = '9091'
    if category == 'Редукторы': 
      category = '9092'
    if category == 'Решетки': 
      category = '9093'
    if category == 'Шестерни': 
      category = '9094'
    if category == 'Шнеки': 
      category = '9095'
    if category == 'Запчасти для посудомоечных машин': 
      category = '9096'
    if category == 'Блокада (замок люка)': 
      category = '9097'
    if category == 'Датчик давления': 
      category = '9098'
    if category == 'Кнопка сетевая': 
      category = '9099'
    if category == 'Насос сливной, корпус насоса': 
      category = '9100'
    if category == 'Прессостат (датчик уровня воды)': 
      category = '9101'
    if category == 'Уплотнительная резина дверцы': 
      category = '9102'
    if category == 'Запчасти для СВЧ-печей': 
      category = '9103'
    if category == 'Cлюда в плитах': 
      category = '9104'
    if category == 'Диоды': 
      category = '9105'
    if category == 'Клавиатуры (сенсорные панели)': 
      category = '9106'
    if category == 'Кнопки открывания двери': 
      category = '9107'
    if category == 'Колпачки для магнетрона': 
      category = '9108'
    if category == 'Конденсаторы': 
      category = '9109'
    if category == 'Крючки двери': 
      category = '9110'
    if category == 'Куплеры (муфты)': 
      category = '9111'
    if category == 'Лампочки': 
      category = '9112'
    if category == 'Магнетроны': 
      category = '9113'
    if category == 'Моторы (двигатели)': 
      category = '9114'
    if category == 'Предохранители': 
      category = '9115'
    if category == 'Роллеры': 
      category = '9116'
    if category == 'Таймеры механические': 
      category = '9117'
    if category == 'Тарелки': 
      category = '9118'
    if category == 'Термопредохранители': 
      category = '9119'
    if category == 'Трансформаторы': 
      category = '9120'
    if category == 'Запчасти для соковыжималок': 
      category = '9121'
    if category == 'Запчасти для тепловентиляторов и масляных обогревателей': 
      category = '9122'
    if category == 'Запчасти для хлебопечек': 
      category = '9123'
    if category == 'Валы': 
      category = '9124'
    if category == 'Втулки': 
      category = '9125'
    if category == 'Лопатки': 
      category = '9126'
    if category == 'Ремни': 
      category = '9127'
    if category == 'Сальники': 
      category = '9128'
    if category == 'Шестерни': 
      category = '9129'
    if category == 'Запчасти для электроутюгов': 
      category = '9130'
    if category == 'Запчасти для электрочайников': 
      category = '9131'
    if category == 'Запчасти для пылесосов': 
      category = '9132'
    if category == 'Двигатели': 
      category = '9133'
    if category == 'Двигатели пылесоса 1200Вт': 
      category = '9134'
    if category == 'Двигатели пылесоса 1400Вт': 
      category = '9135'
    if category == 'Двигатели пылесоса 1500Вт': 
      category = '9136'
    if category == 'Двигатели пылесоса 1600Вт': 
      category = '9137'
    if category == 'Двигатели пылесоса 1800Вт': 
      category = '9138'
    if category == 'Двигатели пылесоса 2000Вт': 
      category = '9139'
    if category == 'Двигатели пылесоса 2200Вт': 
      category = '9140'
    if category == 'Двигатели пылесоса 2400Вт': 
      category = '9141'
    if category == 'Держатель мешка': 
      category = '9142'
    if category == 'Кнопки': 
      category = '9143'
    if category == 'Крепление шланга': 
      category = '9144'
    if category == 'Мешки': 
      category = '9145'
    if category == 'Модули': 
      category = '9146'
    if category == 'НЕРА фильтр': 
      category = '9147'
    if category == 'Фильтр': 
      category = '9148'
    if category == 'Шланги': 
      category = '9149'
    if category == 'Щетки': 
      category = '9150'
    if category == 'Запчасти для стиральных машин': 
      category = '9151'
    if category == 'Активатор (ребро) барабана': 
      category = '9152'
    if category == 'Активаторы барабана Ardo': 
      category = '9153'
    if category == 'Активаторы барабана Beko': 
      category = '9154'
    if category == 'Активаторы барабана Candy': 
      category = '9155'
    if category == 'Активаторы барабана Electrolux, AEG, Zanussi': 
      category = '9156'
    if category == 'Активаторы барабана Gorenje': 
      category = '9157'
    if category == 'Активаторы барабана Indesit, Ariston': 
      category = '9158'
    if category == 'Активаторы барабана LG': 
      category = '9159'
    if category == 'Активаторы барабана Samsung': 
      category = '9160'
    if category == 'Активаторы барабана Whirlpool': 
      category = '9161'
    if category == 'Активаторы барабана Атлант': 
      category = '9162'
    if category == 'Амортизатор': 
      category = '9163'
    if category == 'Aмортизаторы Beko': 
      category = '9164'
    if category == 'Aмортизаторы Gorenje': 
      category = '9165'
    if category == 'Aмортизаторы Hansa': 
      category = '9166'
    if category == 'Aмортизаторы Indesit, Ariston, Ardo': 
      category = '9167'
    if category == 'Aмортизаторы LG': 
      category = '9168'
    if category == 'Aмортизаторы Samsung': 
      category = '9169'
    if category == 'Aмортизаторы Whirlpool': 
      category = '9170'
    if category == 'Aмортизаторы Zanussi, Bosch, Candy': 
      category = '9171'
    if category == 'Амортизаторы универсальные': 
      category = '9172'
    if category == 'Подставка-амортизаторы под ножки': 
      category = '9173'
    if category == 'Блок подшипников': 
      category = '9174'
    if category == 'Блоки подшипников Bosch, Siemens': 
      category = '9175'
    if category == 'Блоки подшипников Candy, Hoover': 
      category = '9176'
    if category == 'Блоки подшипников Electrolux, Zanussi, AEG': 
      category = '9177'
    if category == 'Блоки подшипников Indesit, Ariston': 
      category = '9178'
    if category == 'Блоки подшипников Whirlpool, Ardo, Merloni': 
      category = '9179'
    if category == 'Датчик уровня воды, прессостат': 
      category = '9180'
    if category == 'Датчик холла (таходатчик)': 
      category = '9181'
    if category == 'Дверь, загрузочный люк': 
      category = '9182'
    if category == 'Замок, блокировка люка': 
      category = '9183'
    if category == 'Замки блокировки люка AEG, Electrolux, Zanussi, Hansa': 
      category = '9184'
    if category == 'Замки блокировки люка Ardo': 
      category = '9185'
    if category == 'Замки блокировки люка Beko, Vestel': 
      category = '9186'
    if category == 'Замки блокировки люка Bosch, Siemens': 
      category = '9187'
    if category == 'Замки блокировки люка Candy, Hoover': 
      category = '9188'
    if category == 'Замки блокировки люка Fagor': 
      category = '9189'
    if category == 'Замки блокировки люка Gorenje, Metalflex': 
      category = '9190'
    if category == 'Замки блокировки люка Indesit, Ariston': 
      category = '9191'
    if category == 'Замки блокировки люка LG': 
      category = '9192'
    if category == 'Замки блокировки люка Samsung': 
      category = '9193'
    if category == 'Замки блокировки люка Whirpool': 
      category = '9194'
    if category == 'Замки блокировки люка Атлант': 
      category = '9195'
    if category == 'Запчасти для полуавтоматов': 
      category = '9196'
    if category == 'Активаторы': 
      category = '9197'
    if category == 'Амортизаторы': 
      category = '9198'
    if category == 'Двигатели': 
      category = '9199'
    if category == 'Клапана': 
      category = '9200'
    if category == 'Конденсаторы': 
      category = '9201'
    if category == 'Патрубки и шланги': 
      category = '9202'
    if category == 'Подшипниковые узлы': 
      category = '9203'
    if category == 'Пружины клапана': 
      category = '9204'
    if category == 'Редукторы': 
      category = '9205'
    if category == 'Ремни': 
      category = '9206'
    if category == 'Ручки': 
      category = '9207'
    if category == 'Сальники': 
      category = '9208'
    if category == 'Таймеры стирки и отжима': 
      category = '9209'
    if category == 'Шестерни': 
      category = '9210'
    if category == 'Штоки клапана': 
      category = '9211'
    if category == 'Клапан входной': 
      category = '9212'
    if category == 'Кнопки': 
      category = '9213'
    if category == 'Конденсатор': 
      category = '9214'
    if category == 'Крепление люка': 
      category = '9215'
    if category == 'Крестовина барабана': 
      category = '9216'
    if category == 'Крестовины барабана Ardo': 
      category = '9217'
    if category == 'Крестовины барабана Beko': 
      category = '9218'
    if category == 'Крестовины барабана Bosch Siemens': 
      category = '9219'
    if category == 'Крестовины барабана Candy': 
      category = '9220'
    if category == 'Крестовины барабана Electrolux, Zanussi, AEG': 
      category = '9221'
    if category == 'Крестовины барабана Hansa': 
      category = '9222'
    if category == 'Крестовины барабана Indesit, Ariston': 
      category = '9223'
    if category == 'Крестовины барабана LG': 
      category = '9224'
    if category == 'Крестовины барабана Samsung': 
      category = '9225'
    if category == 'Модуль': 
      category = '9226'
    if category == 'Насос (помпа)': 
      category = '9227'
    if category == 'Насос c корпусом': 
      category = '9228'
    if category == 'Ножка': 
      category = '9229'
    if category == 'Опора (суппорт) барабана': 
      category = '9230'
    if category == 'Патрубок': 
      category = '9231'
    if category == 'Подшипник': 
      category = '9232'
    if category == 'Подшипники CX Польша': 
      category = '9233'
    if category == 'Подшипники ISKRA Польша': 
      category = '9234'
    if category == 'Подшипники JUF Китай': 
      category = '9235'
    if category == 'Подшипники SKF Швеция': 
      category = '9236'
    if category == 'Пружина барабана': 
      category = '9237'
    if category == 'Резина люка': 
      category = '9238'
    if category == 'Резины люка Ardo': 
      category = '9239'
    if category == 'Резины люка Ariston, Indesit': 
      category = '9240'
    if category == 'Резины люка Atlant': 
      category = '9241'
    if category == 'Резины люка Beko': 
      category = '9242'
    if category == 'Резины люка Bosch, Siemens': 
      category = '9243'
    if category == 'Резины люка Candy': 
      category = '9244'
    if category == 'Резины люка Gorenie': 
      category = '9245'
    if category == 'Резины люка LG': 
      category = '9246'
    if category == 'Резины люка Miele': 
      category = '9247'
    if category == 'Резины люка Samsung': 
      category = '9248'
    if category == 'Резины люка Whirlpool': 
      category = '9249'
    if category == 'Резины люка Zanussi, Electrolux, AEG': 
      category = '9250'
    if category == 'Ремень приводной': 
      category = '9251'
    if category == 'Ремень приводной 10.. H7': 
      category = '9252'
    if category == 'Ремень приводной 10.. H8': 
      category = '9253'
    if category == 'Ремень приводной 10.. J4': 
      category = '9254'
    if category == 'Ремень приводной 10.. J5': 
      category = '9255'
    if category == 'Ремень приводной 11.. H7': 
      category = '9256'
    if category == 'Ремень приводной 11.. H8': 
      category = '9257'
    if category == 'Ремень приводной 11.. J4': 
      category = '9258'
    if category == 'Ремень приводной 11.. J5': 
      category = '9259'
    if category == 'Ремень приводной 11.. J6': 
      category = '9260'
    if category == 'Ремень приводной 12.. H7': 
      category = '9261'
    if category == 'Ремень приводной 12.. H8': 
      category = '9262'
    if category == 'Ремень приводной 12.. J4': 
      category = '9263'
    if category == 'Ремень приводной 12.. J5': 
      category = '9264'
    if category == 'Ремень приводной 12.. J6': 
      category = '9265'
    if category == 'Ремень приводной 13.. H8': 
      category = '9266'
    if category == 'Ремень приводной 13.. J4': 
      category = '9267'
    if category == 'Ремень приводной 13.. J5': 
      category = '9268'
    if category == 'Ремень приводной 13.. J6': 
      category = '9269'
    if category == 'Ремень приводной 19.. H': 
      category = '9270'
    if category == 'Ремень приводной 3L': 
      category = '9271'
    if category == 'Ремень приводной J3': 
      category = '9272'
    if category == 'Ручка люка (двери)': 
      category = '9273'
    if category == 'Крючки люка (двери)': 
      category = '9274'
    if category == 'Ручки люка (двери) Ardo': 
      category = '9275'
    if category == 'Ручки люка (двери) Ariston, Indesit': 
      category = '9276'
    if category == 'Ручки люка (двери) Beko': 
      category = '9277'
    if category == 'Ручки люка (двери) Bosch Siemens': 
      category = '9278'
    if category == 'Ручки люка (двери) Daewoo, Candy': 
      category = '9279'
    if category == 'Ручки люка (двери) Fagor': 
      category = '9280'
    if category == 'Ручки люка (двери) Gorenje': 
      category = '9281'
    if category == 'Ручки люка (двери) Hansa': 
      category = '9282'
    if category == 'Ручки люка (двери) LG': 
      category = '9283'
    if category == 'Ручки люка (двери) Samsung': 
      category = '9284'
    if category == 'Ручки люка (двери) Whirlpool': 
      category = '9285'
    if category == 'Ручки люка (двери) Zanussi, Electrolux, AEG': 
      category = '9286'
    if category == 'Ручки переключения программ Атлант': 
      category = '9287'
    if category == 'Сальник': 
      category = '9288'
    if category == 'Cальники c внутренним диаметром 20 мм': 
      category = '9289'
    if category == 'Cальники c внутренним диаметром 21 мм': 
      category = '9290'
    if category == 'Cальники c внутренним диаметром 22 мм': 
      category = '9291'
    if category == 'Cальники c внутренним диаметром 25 мм': 
      category = '9292'
    if category == 'Cальники c внутренним диаметром 28 мм': 
      category = '9293'
    if category == 'Cальники c внутренним диаметром 30 мм': 
      category = '9294'
    if category == 'Cальники c внутренним диаметром 32 мм': 
      category = '9295'
    if category == 'Cальники c внутренним диаметром 34 мм': 
      category = '9296'
    if category == 'Cальники c внутренним диаметром 35 мм': 
      category = '9297'
    if category == 'Cальники c внутренним диаметром 37 мм': 
      category = '9298'
    if category == 'Cальники c внутренним диаметром 40 мм': 
      category = '9299'
    if category == 'Cальники c внутренним диаметром 41 мм': 
      category = '9300'
    if category == 'Cальники c внутренним диаметром 42 мм': 
      category = '9301'
    if category == 'Cальники c внутренним диаметром 47 мм': 
      category = '9302'
    if category == 'Cальники c внутренним диаметром 50 мм': 
      category = '9303'
    if category == 'Cальники c внутренним диаметром 8-15 мм': 
      category = '9304'
    if category == 'Сальники V-RING': 
      category = '9305'
    if category == 'Сальники насоса': 
      category = '9306'
    if category == 'Смазка для сальников': 
      category = '9307'
    if category == 'Температурный датчик': 
      category = '9308'
    if category == 'Термостат': 
      category = '9309'
    if category == 'ТЭН , нагревательный элемент': 
      category = '9310'
    if category == 'Датчики температуры в ТЭН': 
      category = '9311'
    if category == 'ТЭНы Ardo': 
      category = '9312'
    if category == 'ТЭНы Bosch Maxx, Siemens': 
      category = '9313'
    if category == 'ТЭНы Candy': 
      category = '9314'
    if category == 'ТЭНы Hansa': 
      category = '9315'
    if category == 'ТЭНы Indesit Ariston': 
      category = '9316'
    if category == 'ТЭНы LG':	
      category = '9317'
    if category == 'ТЭНы Samsung':	
      category = '9318'
    if category == 'ТЭНы Whirpool, Electrolux, Zanussi':	
      category = '9319'
    if category == 'ТЭНы Атлант':	
      category = '9320'
    if category == 'Фильтр помповый':	
      category = '9321'
    if category == 'Фильтр сетевой':	
      category = '9322'
    if category == 'Химия':	
      category = '9323'
    if category == 'Шкив':	
      category = '9324'
    if category == 'Щетка двигателя':	
      category = '9325'
    if category == 'Запчасти для холодильников':	
      category = '9326'
    if category == 'Вентиляторы No Frost':	
      category = '9327'
    if category == 'Воздушные заслонки':	
      category = '9328'
    if category == 'Выключатели света':	
      category = '9329'
    if category == 'Датчики':	
      category = '9330'
    if category == 'Двигатели':	
      category = '9331'
    if category == 'Испарители':	
      category = '9332'
    if category == 'Клапана шредера':	
      category = '9333'
    if category == 'Кнопки':	
      category = '9334'
    if category == 'Комплектующие для монтажа кондиционеров':	
      category = '9335'
    if category == 'Кронштейны':	
      category = '9336'
    if category == 'Лента термоизоляционная':	
      category = '9337'
    if category == 'Термоизолятор K-FLEX':	
      category = '9338'
    if category == 'Труба медная кондиционерная':	
      category = '9339'
    if category == 'Компрессоры':	
      category = '9340'
    if category == 'Краны для фреоновых баллонов':	
      category = '9341'
    if category == 'Крепление (петля) двери':	
      category = '9342'
    if category == 'Лампочки':	
      category = '9343'
    if category == 'Модули управления':	
      category = '9344'
    if category == 'Осевые вентиляторы универсальные':	
      category = '9345'
    if category == 'Панели ящиков':	
      category = '9346'
    if category == 'Припои для пайки':	
      category = '9347'
    if category == 'Пускозащитное реле':	
      category = '9348'
    if category == 'Расходные материалы':	
      category = '9349'
    if category == 'Реле тепловое':	
      category = '9350'
    if category == 'Ручка двери':	
      category = '9351'
    if category == 'Термостаты':	
      category = '9352'
    if category == 'Термостаты-таймеры (темпоризаторы)':	
      category = '9353'
    if category == 'Труба медная капиллярная':	
      category = '9354'
    if category == 'Тэны оттайки':	
      category = '9355'
    if category == 'Уплотнительная резина':	
      category = '9356'
    if category == 'Фильтра осушители':	
      category = '9357'
    if category == 'Фреоновые и вакуумные масла':	
      category = '9358'
    if category == 'Фреоны':	
      category = '9359'
    return category
  
  def get_description(self, *args, **kwargs):
    soup = args[0]
    desc =  soup.find('div', id='tab-description').text
    return desc
  
  def get_imgs(self, *args, **kwargs):
    soup = args[0]
    # small_img = args[1]
    # return print('sss',small_img)
    product = soup.find('div', class_='product-info')
    img = []
    for i in product.find_all('a', class_='fancybox'):
      img.append(i.get('href'))
    return ', '.join(img)
  
  def get_articule(self, *args, **kwargs):
    soup = args[0]
    product = soup.find('div', class_='product-info')
    articule  = product.find('div', class_='description').text.strip().split('\n')[0].split(':')[1].strip()
    with open('remza.csv', 'r') as file:
      if articule in file.read():
        articule += '__2'
    with open('remza.csv', 'r') as file:
      if articule in file.read():
        articule = articule[0:-3]+'__3'
    with open('remza.csv', 'r') as file:
      if articule in file.read():
        articule = articule[0:-3]+'__4'
    return articule
  
  def get_price(self, *args, **kwargs):
    soup = args[0]
    product = soup.find('div', class_='product-info')
    price = product.find('div' ,class_='price').text.strip().split(' ')[0].replace('грн.', "")
    return price
  
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
    # category     = self.get_category(args[0], args[1])
    category = kwargs['category']
    imgs         = self.get_imgs(soup)
    articule     = self.get_articule(soup)
    desc         = self.get_description(soup)
    price        = self.get_price(soup)
    availability = '+' #self.get_availability(soup)
    data         = self.get_fieldnames()
    data['Код_товара']           = articule
    data['Название_позиции']     = name
    data['Описание']             = desc
    data['Тип_товара']           = 'r'
    data['Цена']                 = price
    data['Валюта']               = 'UAH'
    data['Единица_измерения']    = 'шт'
    data['Продукт_на_сайте']     = url
    data['Идентификатор_группы'] = category
    data['Идентификатор_товара'] = articule
    data['Ссылка_изображения']   = imgs
    data['Наличие']              = '+'#availability
    print('\n') 
    print("Ссылка: ",url)
    print("Изображения: ", imgs)
    print("Название: ",name)
    print("Артикул: ",articule)
    print("Цена: ",price)
    print("Категория: ",category)
    print("Описание: ",desc)
    print('\n')
    self.write_csv(data=data, filename='remza.csv')
    # self.write_xlsx(data=data, filename='remza_xlsx.xlsx')


if __name__ == '__main__':
  parser = Parser()
  for cat in categories:
    url = cat[0]
    cat_name = cat[2]
    soup = BeautifulSoup(parser.get_html(url), 'lxml')
    products = soup.find('div', class_="product-list").find_all('div', class_='name')
    for product in products:
      link = product.a.get('href')
      try:
        parser.get_product(link, category=cat_name)
      except:pass



  # parser.edit_categories()

  url = 'http://remza.com.ua/sitemap'
  # parser.get_categories(url)
  
  url = 'https://ebearing.com.ua/ru/catalog/cat-198-podshipnik'
  # parser.pagination(url, stop=809, turbo=True)

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

  # parser.get_product(url5)











