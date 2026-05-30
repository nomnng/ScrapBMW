import scrapy, chompjs
from scrapy.http.cookies import CookieJar
from scrapy.http import Response
from bmw_scrapper.items import CarItem


def safe_get(dictionary, keys, default=None):
    # Helper function for getting data from nested dictionary
    current = dictionary
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default


class CarListingSpiderSpider(scrapy.Spider):
    name = "car_listing_spider"
    allowed_domains = ["usedcars.bmw.co.uk"]
    start_urls = ["https://usedcars.bmw.co.uk"]

    ITEMS_PER_PAGE = 23
    PAGES_TO_SCRAP = 5

    def parse(self, response: Response):
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response, response.request)
        cookies_dict = {cookie.name: cookie.value for cookie in cookie_jar}
    
        csrf_token = cookies_dict.get("csrftoken")
        
        if not csrf_token:
            self.logger.error("CSRF Token not found in cookies!")
            return

        self.logger.info(f"Session Cookies: {cookies_dict}")

        for i in range(self.PAGES_TO_SCRAP):
            page = i + 1
            yield response.follow(
                url=f"/vehicle/api/list/?payment_type=cash&size={self.ITEMS_PER_PAGE}&page={page}",
                method="GET",
                headers={
                    "X-Csrftoken": csrf_token,
                    "Content-Type": "application/json"
                },
                callback=self.parse_api_response
            )

    def parse_api_response(self, response: Response):
        json = response.json()
        results = json["results"]
        for item in results:
            advert_id = item["advert_id"]
            yield response.follow(f"/vehicle/{advert_id}", callback=self.parse_car_specs)

    def parse_car_specs(self, response: Response):
        for script in response.css("#main-content > script"):
            script_code = script.get()
            uvl_ad_index = script_code.find("UVL.AD =")
            if uvl_ad_index >= 0:
                uvl_ad_object_str = script_code[uvl_ad_index:]
                try:
                    uvl_ad_object = chompjs.parse_js_object(uvl_ad_object_str)
                except ValueError:
                    self.logger.info("Failed to parse UVL.AD object")
                    continue

                car_item = CarItem()
                car_item["model"] = safe_get(uvl_ad_object, ["title"])
                car_item["name"] = safe_get(uvl_ad_object, ["specification", "derivative"])
                car_item["registration"] = safe_get(uvl_ad_object, ["identification", "registration"])
                car_item["registered"] = safe_get(uvl_ad_object, ["dates", "registration"])
                car_item["mileage"] = safe_get(uvl_ad_object, ["condition_and_state", "mileage"])
                car_item["exterior"] = safe_get(uvl_ad_object, ["colour", "manufacturer_colour"])
                car_item["transmission"] = safe_get(uvl_ad_object, ["specification", "transmission"])
                car_item["upholstery"] = safe_get(uvl_ad_object, ["specification", "interior"])

                car_item["fuel"] = safe_get(uvl_ad_object, ["engine", "fuel"])
                if car_item["fuel"] and car_item["fuel"].lower() == "electric":
                    car_item["range"] = safe_get(uvl_ad_object, ["battery", "range", "value"])
                else:
                    car_item["engine"] = safe_get(uvl_ad_object, ["engine", "size", "cc"])

                yield car_item
                self.logger.info(f"Scraped car: {car_item["registration"]}")
                break

