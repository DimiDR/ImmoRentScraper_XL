# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import googlemaps
import datetime
import shelve
from scrapy.exceptions import DropItem
import sqlite3
from immospider.items import ImmoscoutItem
from scrapy.exporters import CsvItemExporter

# see https://doc.scrapy.org/en/latest/topics/item-pipeline.html#duplicates-filter
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = shelve.open("immo_items.db")

    def process_item(self, item, spider):
        immo_id = item['immo_id']

        if immo_id in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.ids_seen[immo_id] = item
            return item

class SQlitePipeline(object):
# Help in SQlite type definition
# https://www.sqlite.org/datatype3.html
# NULL. The value is a NULL value.
# INTEGER. The value is a signed integer, stored in 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.
# REAL. The value is a floating point value, stored as an 8-byte IEEE floating point number.
# TEXT. The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).
# BLOB. The value is a blob of data, stored exactly as it was input.

    def open_spider(self, spider):
        self.connection = sqlite3.connect("real-estate.db")
        self.c = self.connection.cursor()
        # comment the drop table to always add additional information!!! #########
        #self.c.execute('''DROP TABLE IF EXISTS immoscout''')
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS immoscout(
                    immo_id INTEGER NOT NULL PRIMARY KEY,
                    year TEXT,
                    month TEXT,
                    day TEXT,
                    title TEXT,
                    url TEXT,
                    city TEXT,
                    postcode INTEGER,
                    quarter TEXT,
                    street TEXT,
                    lat REAL,
                    lng REAL,
                    balcony TEXT,
                    builtInKitchen TEXT,
                    energyEfficiencyClass TEXT,
                    cellar TEXT,
                    garden TEXT,
                    guestToilet TEXT,
                    lift TEXT,
                    livingSpace REAL,
                    numberOfRooms REAL,
                    additional_costs REAL,
                    value REAL,
                    house_money REAL,
                    year_of_construction INTEGER,
                    object_description TEXT,
                    area TEXT,
                    additional_info TEXT,
                    equipment TEXT,
                    provision REAL,
                    provision_percent REAL,
                    land_transfer REAL,
                    land_transfer_percent REAL,
                    notary REAL,
                    notary_percent REAL,
                    entry_land REAL,
                    entry_land_percent REAL
                )
            ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        #TODO: implement the 3 values from google. They all should not be empty
        self.c.execute('''
            INSERT OR IGNORE INTO immoscout (
                immo_id, 
                year,
                month,
                day,
                title, 
                url, 
                city, 
                postcode, 
                quarter, 
                street, 
                lat, 
                lng,
                balcony, 
                builtInKitchen, 
                energyEfficiencyClass, 
                cellar, 
                garden, 
                guestToilet, 
                lift, 
                livingSpace, 
                numberOfRooms, 
                additional_costs, 
                value,
                house_money,
                year_of_construction,
                object_description,
                area,
                additional_info,
                equipment,
                provision,
                provision_percent,
                land_transfer,
                land_transfer_percent,
                notary,
                notary_percent,
                entry_land,
                entry_land_percent
                ) VALUES(?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?,?,?,?,
                        ?,?)
                ''', (
                    item['immo_id'],
                    item['year'],
                    item['month'],
                    item['day'],
                    item['title'],
                    item['url'],
                    item['city'],
                    item['postcode'],
                    item['quarter'],
                    item['street'],
                    item['lat'],
                    item['lng'],
                    item['balcony'],
                    item['builtInKitchen'],
                    item['energyEfficiencyClass'],
                    item['cellar'],
                    item['garden'],
                    item['guestToilet'],
                    item['lift'],
                    item['livingSpace'],
                    item['numberOfRooms'],
                    item['additional_costs'],
                    item['value'],
                    item['house_money'],
                    item['year_of_construction'],
                    item['object_description'],
                    item['area'],
                    item['additional_info'],
                    item['equipment'],
                    item['provision'],
                    item['provision_percent'],
                    item['land_transfer'],
                    item['land_transfer_percent'],
                    item['notary'],
                    item['notary_percent'],
                    item['entry_land'],
                    item['entry_land_percent'],
        ))
        self.connection.commit()
        return item

class GooglemapsPipeline(object):

    # see https://stackoverflow.com/questions/14075941/how-to-access-scrapy-settings-from-item-pipeline
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        gm_key = settings.get("GM_KEY")
        return cls(gm_key)

    def __init__(self, gm_key):
        if gm_key:
            self.gm_client = googlemaps.Client(gm_key)

    def _get_destinations(self, spider):
        destinations = []

        if hasattr(spider, "dest"):
            mode = getattr(spider, "mode", "driving")
            destinations.append((spider.dest, mode))
        if hasattr(spider, "dest2"):
            mode2 = getattr(spider, "mode2", "driving")
            destinations.append((spider.dest2, mode2))
        if hasattr(spider, "dest3"):
            mode3 = getattr(spider, "mode3", "driving")
            destinations.append((spider.dest3, mode3))

        return destinations

    def _next_monday_eight_oclock(self, now):
        monday = now - datetime.timedelta(days=now.weekday())
        if monday < monday.replace(hour=8, minute=0, second=0, microsecond=0):
            return monday.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            return (monday + datetime.timedelta(weeks=1)).replace(hour=8, minute=0, second=0, microsecond=0)

    def process_item(self, item, spider):
        if hasattr(self, "gm_client"):
            # see https://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
            next_monday_at_eight = (self._next_monday_eight_oclock(datetime.datetime.now())
                                         - datetime.datetime(1970, 1, 1)).total_seconds()

            destinations = self._get_destinations(spider)
            travel_times = []
            for destination, mode in destinations:
                result = self.gm_client.distance_matrix(item["address"],
                                                              destination,
                                                              mode=mode,
                                                              departure_time = next_monday_at_eight)
                #  Extract the travel time from the result set
                travel_time = None
                if result["rows"]:
                    if result["rows"][0]:
                        elements = result["rows"][0]["elements"]
                        if elements[0] and "duration" in elements[0]:
                            duration = elements[0]["duration"]
                            if duration:
                                travel_time = duration["value"]

                if travel_time is not None:
                    print(destination, mode, travel_time/60.0)
                    travel_times.append(travel_time/60.0)

            item["time_dest"] = travel_times[0] if len(travel_times) > 0 else None
            item["time_dest2"] = travel_times[1] if len(travel_times) > 1 else None
            item["time_dest3"] = travel_times[2] if len(travel_times) > 2 else None

        return item

class JsonPipeline(object):
    def __init__(self):
        self.file = open("books.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class CsvPipeline(object):
    def __init__(self):
        self.file = open("booksdata.csv", 'wb')
        self.exporter = CsvItemExporter(self.file, unicode)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def create_valid_csv(self, item):
        for key, value in item.items():
            is_string = (isinstance(value, basestring))
            if (is_string and ("," in value.encode('utf-8'))):
                item[key] = "\"" + value + "\""