import scrapy, chompjs
from scrapy.http.cookies import CookieJar
from scrapy.http import Response


class CarListingSpiderSpider(scrapy.Spider):
    name = "car_listing_spider"
    allowed_domains = ["usedcars.bmw.co.uk"]
    start_urls = ["https://usedcars.bmw.co.uk"]

    ITEMS_PER_PAGE = 1

    def parse(self, response: Response):
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response, response.request)
        cookies_dict = {cookie.name: cookie.value for cookie in cookie_jar}
    
        csrf_token = cookies_dict.get("csrftoken")
        
        if not csrf_token:
            self.logger.error("CSRF Token not found in cookies!")
            return

        self.logger.info(f"Session Cookies: {cookies_dict}")

        yield response.follow(
            url=f"/vehicle/api/list/?payment_type=cash&size={self.ITEMS_PER_PAGE}",
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
            yield {
                "advert_id": advert_id,
                "model": item["title"],
                "name": item["derivative"],
            }

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
                yield uvl_ad_object
                break

