from tkinter import EXCEPTION
from django.conf import settings

from .models import Court, Jurisdiction
from .utils import get_digits, get_range

from bs4 import BeautifulSoup as Bs

import requests
import xlsxwriter


class Service:
    base_url = 'https://mirsud.spb.ru/court-sites/{}/'

    @staticmethod
    def create_court(data: dict, url: str) -> Court:
        court, created = Court.objects.get_or_create(name_judicial_precinct=data['name'])

        court.address = data['address']
        court.judge_full_name = data['judge_name']
        court.clerk_full_name = data['clerk_name']
        court.assistant_full_name = data['assistant_name']
        court.region = 'Санкт-Петербург'
        court.judge_email = data['email']
        court.district = data['district']
        court.site = url

        try:
            phones = data['phone']
            court.type_phone_1 = 'Телефон'
            court.phone_1 = get_digits(phones[0])

            court.type_phone_2 = 'Факс'
            court.phone_2 = get_digits(phones[1])
        except IndexError:
            court.type_phone_1 = 'Телефон'
            court.phone_1 = get_digits(data['phone'][0])

        court.save()
        return court

    @staticmethod
    def create_jurisdictions(data: list, court: Court):
        objects = []
        for podsud in data:
            try:
                street = podsud[0]
                obj1 = get_range(podsud[1], court, street)
                obj2 = get_range(podsud[2], court, street)        
                if obj1:
                    objects.append(obj1)
                if obj2:
                    objects.append(obj2)
                    
            except IndexError:
                continue

        Jurisdiction.objects.bulk_create(objects)

    @staticmethod
    def get_court_data_from_html(soup: Bs) -> dict:
        data = {}
        phone = soup.find('div', class_='telfax').find('p').text.split(',')
        data['name'] = soup.find('main').find('h1').text
        data['address'] = soup.find('div', class_='adress-fact').find('p').text
        data['phone'] = phone
        try:
            data['email'] = soup.find('a', class_='link__mail').text.replace(' ', '')
        except AttributeError:
            data['email'] = ''

        about_sector = soup.find('article', class_='about-sector').findAll('p')
        data['judge_name'] = about_sector[0].text
        try:
            data['clerk_name'] = about_sector[1].text
            data['assistant_name'] = about_sector[2].text
            data['district'] = about_sector[3].text
        except IndexError:
            data['clerk_name'] = ''
            data['assistant_name'] = ''
            data['district'] = ''
        return data

    @staticmethod
    def get_jurisdiction_data_from_html(soup: Bs) -> list:
        territorial = soup.find('article', class_='territorial').findAll('tr')
        data = []
        for tr in territorial:
            obj = []
            for td in tr.findAll('td'):
                obj.append(td.text)

            data.append(obj)

        return data

    @staticmethod
    def write_courts_sheet(workbook: xlsxwriter.Workbook) -> xlsxwriter.workbook.Worksheet:
        courts = workbook.add_worksheet('REC')
        courts.write(0, 0, 'Наименование судебного участка')
        courts.write(0, 1, 'КодГАСРФ')
        courts.write(0, 2, 'Сайт')
        courts.write(0, 3, 'Регион')
        courts.write(0, 4, 'Адрес')
        courts.write(0, 5, 'Полное ФИО Судьи')
        courts.write(0, 6, 'Email судьи')
        courts.write(0, 7, 'ФИО ПомощникаСудьи')
        courts.write(0, 8, 'ФИО Секретаря судебного участка')
        courts.write(0, 9, 'ФИО Секретаря судебного заседани')
        courts.write(0, 10, 'Вид телефона1')
        courts.write(0, 11, 'Телефон1')
        courts.write(0, 12, 'Вид телефона2')
        courts.write(0, 13, 'Телефон2')
        courts.write(0, 14, 'Вид телефона3')
        courts.write(0, 15, 'Телефон3')

        return courts

    @staticmethod
    def write_jurisdictions_sheet(workbook: xlsxwriter.Workbook) -> xlsxwriter.workbook.Worksheet:
        jurisdictions = workbook.add_worksheet('Тер подсудность')
        jurisdictions.write(0, 1, 'КодГАСРФ')
        jurisdictions.write(0, 2, 'Сайт')
        jurisdictions.write(0, 3, 'Регион')
        jurisdictions.write(0, 4, 'Район, населенный пункт')
        jurisdictions.write(0, 5, 'микрорайон, улица, прочие адресные указатели')
        jurisdictions.write(0, 6, 'номер дома, если в подсудность входят единичные дома')
        jurisdictions.write(0, 7, 'номер дома начала интервала, если в подсудность входит интервал домов')
        jurisdictions.write(0, 8, 'номер дома конца интервала')
        jurisdictions.write(0, 9, 'номер дома конца интервала')
        jurisdictions.write(0, 9, 'Четность (при наличии), -1 - не четные, 1 - четные, 0 - все')
        jurisdictions.write(0, 10, 'Номера домов исключений из интервала (если имеются)')

        return jurisdictions

    def get_content(self):
        for page in range(1, 250):
            url = self.base_url.format(f'{page}')
            page = requests.get(url)
            soup = Bs(page.text, 'html.parser')

            # Данные по судебному участку
            court_data = self.get_court_data_from_html(soup)
            court = self.create_court(court_data, url)

            # Данные по территориальной подсудности
            jurisdiction = self.get_jurisdiction_data_from_html(soup)

            self.create_jurisdictions(jurisdiction, court)

    def get_xlsx(self):
        workbook = xlsxwriter.Workbook(f'{settings.BASE_DIR}/xlsx/data.xlsx')

        courts = self.write_courts_sheet(workbook)
        jurisdiction = self.write_jurisdictions_sheet(workbook)

        courts_objects = Court.objects.all().prefetch_related('jurisdictions')

        row = 1
        col = 0
        for i in courts_objects:
            courts.write(row, col, i.name_judicial_precinct)
            courts.write(row, col + 1, i.code_GASRF)
            courts.write(row, col + 2, i.site)
            courts.write(row, col + 3, i.region)
            courts.write(row, col + 4, i.address)
            courts.write(row, col + 5, i.judge_full_name)
            courts.write(row, col + 6, i.judge_email)
            courts.write(row, col + 7, i.assistant_full_name)
            courts.write(row, col + 8, i.clerk_full_name)
            courts.write(row, col + 9, i.secretary_court_session)
            courts.write(row, col + 10, i.type_phone_1)
            courts.write(row, col + 11, i.phone_1)
            courts.write(row, col + 12, i.type_phone_2)
            courts.write(row, col + 13, i.phone_2)
            courts.write(row, col + 14, i.type_phone_3)
            courts.write(row, col + 15, i.phone_3)

            row += 1

        row_1 = 1

        for i in courts_objects:
            for a in i.jurisdictions.all():
                jurisdiction.write(row_1, col, i.name_judicial_precinct)
                jurisdiction.write(row_1, col + 1, i.code_GASRF)
                jurisdiction.write(row_1, col + 2, i.site)
                jurisdiction.write(row_1, col + 3, i.region)
                jurisdiction.write(row_1, col + 4, i.district)
                jurisdiction.write(row_1, col + 5, a.street)
                jurisdiction.write(row_1, col + 6, a.house_number)
                jurisdiction.write(row_1, col + 7, a.start_house_number)
                jurisdiction.write(row_1, col + 8, a.end_house_number)
                jurisdiction.write(row_1, col + 9, a.parity)
                jurisdiction.write(row_1, col + 10, a.excluded_houses)

                row_1 += 1

        workbook.close()
