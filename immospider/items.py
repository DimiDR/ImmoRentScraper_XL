# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmoscoutItem(scrapy.Item):
    # define the fields for your item here like:
    #  name = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    day = scrapy.Field()
    immo_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    city = scrapy.Field()
    postcode = scrapy.Field()
    quarter = scrapy.Field()
    street = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()
    balcony = scrapy.Field()
    realtorCompanyName = scrapy.Field()
    builtInKitchen = scrapy.Field()
    energyEfficiencyClass = scrapy.Field()
    cellar = scrapy.Field()
    garden = scrapy.Field()
    guestToilet = scrapy.Field()
    lift = scrapy.Field()
    livingSpace = scrapy.Field()
    numberOfRooms = scrapy.Field()
    additional_costs = scrapy.Field()
    value = scrapy.Field()

    house_money = scrapy.Field()
    year_of_construction = scrapy.Field()
    object_description = scrapy.Field()
    area = scrapy.Field()
    additional_info = scrapy.Field()
    equipment = scrapy.Field()
    provision = scrapy.Field()
    provision_percent = scrapy.Field()
    land_transfer = scrapy.Field()
    land_transfer_percent = scrapy.Field()
    notary = scrapy.Field()
    notary_percent = scrapy.Field()
    entry_land = scrapy.Field()
    entry_land_percent = scrapy.Field()
    rent = scrapy.Field()


