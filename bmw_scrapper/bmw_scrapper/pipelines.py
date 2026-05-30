# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from itemadapter import ItemAdapter


class SQLitePipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect("bmw_cars.db")
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                registration TEXT PRIMARY KEY NOT NULL,
                model TEXT,
                name TEXT,
                mileage TEXT,
                registered TEXT,
                engine TEXT,
                range TEXT,
                exterior TEXT,
                fuel TEXT,
                transmission TEXT,
                upholstery TEXT
            )
        """)
        self.connection.commit()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT OR IGNORE INTO cars (
                model, name, mileage, registered, engine, range, 
                exterior, fuel, transmission, registration, upholstery
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("model"),
            item.get("name"),
            item.get("mileage"),
            item.get("registered"),
            item.get("engine"),
            item.get("range"),
            item.get("exterior"),
            item.get("fuel"),
            item.get("transmission"),
            item.get("registration"),
            item.get("upholstery")
        ))
        self.connection.commit()
        return item
