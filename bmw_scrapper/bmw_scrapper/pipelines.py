import sqlite3, logging
from scrapy.exceptions import DropItem


class DataProcessingPipeline:
    REQUIRED_FIELDS = ["model", "name", "registration"]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        for field in self.REQUIRED_FIELDS:
            if not item.get(field):
                msg = f"Missing required field '{field}' in item: {item}"
                self.logger.warning(msg)
                raise DropItem(msg)

        if item.get("mileage"):
            try:
                mileage_str = str(item["mileage"]).replace(",", "")
                item["mileage"] = int(mileage_str)
            except ValueError:
                msg = f"Invalid mileage format: {item["mileage"]}. Dropping item."
                self.logger.warning(msg)
                raise DropItem(msg)

        if item.get("fuel"):
            item["fuel"] = item["fuel"].lower()

        return item


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
