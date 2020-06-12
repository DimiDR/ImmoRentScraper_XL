# -*- coding: utf-8 -*-
import scrapy
import json, urllib.request
from immospider.items import ImmoscoutItem
import requests
import datetime
# API Call
import http.client
import mimetypes
import json

class ImmoscoutSpider(scrapy.Spider):
    name = "immoscout"
    allowed_domains = ["immobilienscout24.de"]
    # start_urls = ['https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin']
    # start_urls = ['https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin/Lichterfelde-Steglitz_Nikolassee-Zehlendorf_Dahlem-Zehlendorf_Zehlendorf-Zehlendorf/2,50-/60,00-/EURO--800,00/-/-/']

    # The immoscout search results are stored as json inside their javascript. This makes the parsing very easy.
    # I learned this trick from https://github.com/balzer82/immoscraper/blob/master/immoscraper.ipynb .
    script_xpath = './/script[contains(., "IS24.resultList")]' #JavaScript on search list page
    next_xpath = '//div[@id = "pager"]/div/a/@href' #go to next page

    def start_requests(self):
        yield scrapy.Request(self.url)

    def parse(self, response):

        #print(response.url)

        for line in response.xpath(self.script_xpath).extract_first().split('\n'):
            if line.strip().startswith('resultListModel'):
                immo_json = line.strip()
                immo_json = json.loads(immo_json[17:-1]) # everything element including #18..(last-1)

                #TODO: On result pages with just a single result resultlistEntry is not a list, but a dictionary.
                #TODO: So extracting data will fail.
                for result in immo_json["searchResponseModel"]["resultlist.resultlist"]["resultlistEntries"][0]["resultlistEntry"]:

                    item = ImmoscoutItem() #define new field if needed here

                    data = result["resultlist.realEstate"]

                    #General Information
                    item['immo_id'] = data['@id']
                    item['title'] = data['title']
                    item['url'] = response.urljoin("/expose/" + str(data['@id']))
                    #Adress
                    address = data['address']
                    try:
                        item['city'] = address['city']
                    except:
                        item['city'] = ""
                    try:
                        item['postcode'] = address['postcode']
                    except:
                        item['postcode'] = ""
                    try:
                        item['quarter'] = address['quarter']
                    except:
                        item['quarter'] = ""
                    try:
                        item['street'] = address['street']
                    except:
                        item['street'] = ""
                    try:
                        item['lat'] = address['wgs84Coordinate']['latitude']
                        item['lng'] = address['wgs84Coordinate']['longitude']
                    except Exception as e:
                        # print(e)
                        item['lat'] = "0.0"
                        item['lng'] = "0.0"
                    #Additions
                    if "realtorCompanyName" in data:
                        item["realtorCompanyName"] = data["realtorCompanyName"]
                    else:
                        item["realtorCompanyName"] = ""
                    if "balcony" in data:
                        item["balcony"] = data["balcony"]
                    else:
                        item["balcony"] = "false"
                    if "builtInKitchen" in data:
                        item["builtInKitchen"] = data["builtInKitchen"]
                    else:
                        item["builtInKitchen"] = "false"
                    if "energyEfficiencyClass" in data:
                        item["energyEfficiencyClass"] = data["energyEfficiencyClass"]
                    else:
                        item["energyEfficiencyClass"] = ""
                    if "cellar" in data:
                        item["cellar"] = data["cellar"] 
                    else:
                        item["cellar"] = "false"
                    if "garden" in data:
                        item["garden"] = data["garden"] 
                    else:
                        item["garden"] = "false"
                    if "guestToilet" in data:
                        item["guestToilet"] = data["guestToilet"]
                    else:
                        item["guestToilet"] = "false"
                    if "lift" in data:
                        item["lift"] = data["lift"]
                    else:
                        item["lift"] = "false"
                    #if "privateOffer" in data:
                    #    item["privateOffer"] = data["privateOffer"]
                    #else:
                    #    item["privateOffer"] = "false"
                    item["livingSpace"] = data["livingSpace"]
                    item["numberOfRooms"] = data["numberOfRooms"]
                    if "calculatedPrice" in data:
                        item["additional_costs"] = (data["calculatedPrice"]["value"] - data["price"]["value"])
                    else:
                        item["additional_costs"] = "0.0"
                    #Price
                    price = data["price"]
                    item["value"] = price["value"]

                    #Time Stamp
                    now = datetime.datetime.now()
                    item["year"] = now.year
                    item["month"] = now.month
                    item["day"] = now.day

                    yield response.follow(url=item['url'], callback=self.parse_property, meta={'item': item})
                    #yield response.follow(url='https://www.immobilienscout24.de/expose/106972809', callback=self.parse_property, meta={'item': item})
                    #yield item

        next_page_list = response.xpath(self.next_xpath).extract()
        if next_page_list:
            next_page = next_page_list[-1]
            print("Scraping next page", next_page)
            if next_page:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    # activate when updating the texts. Will be done in seperate DB
    def parse_property(self, response):
        item = response.request.meta['item']
        try:
            house_money = response.xpath("//dd[contains(@class, 'is24qa-hausgeld grid-item three-fifths')]/text()").extract_first()
            house_money = house_money.split()[0]
            house_money = house_money.replace(',', '.', 1)
        except:
            house_money = '0'
        try:
            rent = response.xpath("//dd[contains(@class, 'is24qa-mieteinnahmen-pro-monat grid-item three-fifths')]/text()").extract_first()
            rent = rent.split()[0]
            rent = rent.replace(',', '.', 1)
        except:
            rent = '0'
        year_of_construction = response.xpath("//dd[contains(@class, 'is24qa-baujahr')]/text()").extract_first()
        object_description = response.xpath("//pre[@class='is24qa-objektbeschreibung text-content short-text']/text()").extract_first()
        area = response.xpath("//pre[@class='is24qa-lage text-content short-text']/text()").extract_first()
        additional_info = response.xpath("//pre[@class='is24qa-sonstiges text-content short-text']/text()").extract_first()
        equipment = response.xpath("//pre[contains(@class, 'is24qa-ausstattung')]/text()").extract_first()
        item.update({'house_money': house_money})
        item.update({'year_of_construction': year_of_construction})
        item.update({'object_description': object_description})
        item.update({'area': area})
        item.update({'additional_info': additional_info})
        item.update({'equipment': equipment})
        item.update({'rent': rent})
        # api for additional costs
        # will not work if loanAmount is too small
        # get_addition_price auflösen und hier einen API Callback einbauen direkt
        #url = 'https://www.immobilienscout24.de/baufinanzierung-api/restapi/api/financing/construction/v1.0/monthlyrate?exposeId={}'.format(item['immo_id'])
        #url = 'https://www.immobilienscout24.de/baufinanzierung-api/restapi/api/financing/construction/v1.0/monthlyrate?exposeId=115603829'
        data = self.api_call(item['immo_id'])
        if data == 'Error':
            provision = '0.0'
            provision_percent = '0.0'
            land_transfer = '0.0'
            land_transfer_percent = '0.0'
            notary = '0.0'
            notary_percent = '0.0'
            entry_land = '0.0'
            entry_land_percent = '0.0'
        else:
            provision = data['additionalCosts']['brokerCommission']
            provision_percent = data['additionalCosts']['brokerCommissionPercentage']
            land_transfer = data['additionalCosts']['landTransfer']
            land_transfer_percent = data['additionalCosts']['landTransferPercentage']
            notary = data['additionalCosts']['notaryCosts']
            notary_percent = data['additionalCosts']['notaryCostsPercentage']
            entry_land = data['additionalCosts']['entryLandRegister']
            entry_land_percent = data['additionalCosts']['entryLandRegisterPercentage']
        
        item.update({'provision': provision})
        item.update({'provision_percent': provision_percent})
        item.update({'land_transfer': land_transfer})
        item.update({'land_transfer_percent': land_transfer_percent})
        item.update({'notary': notary})
        item.update({'notary_percent': notary_percent})
        item.update({'entry_land': entry_land})
        item.update({'entry_land_percent': entry_land_percent})

        #yield response.follow(url=url, callback=self.get_addition_price, meta={'item': item})
        yield item

    def api_call(self, immo_id):
        conn = http.client.HTTPSConnection("www.immobilienscout24.de")
        payload = ''
        headers = {}
        conn.request("GET", '/baufinanzierung-api/restapi/api/financing/construction/v1.0/monthlyrate?exposeId={}'.format(immo_id), payload, headers)
        res = conn.getresponse()
        conn.close
        if res.code != 200:
            return 'Error'
        else:
            data = res.read()
            return json.loads(data)