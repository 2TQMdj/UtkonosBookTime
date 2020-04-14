import requests
import json
import time
import datetime
from pyquery import PyQuery

token = "???" # Токен для авторизации
addressNumberToUse = 0 # Номер по порядку из списка адресов
daysToReserve = [14,15] # Какой день месяца искать для бронирования


# Поиск адресов
addresses = []
response = requests.get('https://www.utkonos.ru/ordering/interval',
    headers={"Cookie":"Utk_SssTkn=" + token})
data = response.content

pq = PyQuery(data)
if len(pq('.contact_data_container').text()) == 0:
    exit("Ошибка авторизации, проверьте токен.")

inaddresses = pq.items('.address_list .address_receipt_item-row')
for address in inaddresses:
    name = address('.address_receipt_item-title').attr('title')
    id = address('.action_edit').attr('data-address_id')
    addresses.append({"id":id, "name": name})

if len(addresses) < 1:
    exit("В профиле отсутствуют адреса доставки, добавьте минимум один.")

print("Найдены адреса:")
for address in addresses:
    print(" "+address.get("name"))

address = addresses[addressNumberToUse]
addressId = address.get("id")
print("Будет использован адрес "+address.get("name"))


# Поиск доступных временных интервалов
while True:
    response = requests.get('https://www.utkonos.ru/utkax.php/intervals/response?address_id='+addressId)
    data = response.content

    data = json.loads(data)
    intervals = data['ajax']['intervals']['items']

    for interval in intervals:

        if(len(interval['disable_reasons']) == 0):
            id = interval['id']
            date = interval['delivery_date']
            day = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").day

            index = None
            try:
                index = daysToReserve.index(day)
            except:
                pass

            if index != None:
                response = requests.get('https://www.utkonos.ru/utkax.php/intervals/reserv?order_recipient=&options%5Baddress_id%5D='+addressId+'&interval_id='+id,
                    headers={"Cookie":"Utk_SssTkn=" + token})
                print("Успешно зарезервировано время " + date)
                exit();

            print("Пропуск неподходящей даты " + date)

    print("Обновление...")
    time.sleep(3)
