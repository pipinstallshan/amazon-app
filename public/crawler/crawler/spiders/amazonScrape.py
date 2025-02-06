import json
import time
import random
import scrapy
from collections import defaultdict
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from crawler.modules.product_model import Product
from crawler.modules.file_saver import save_to_json
from crawler.modules.json_reader import read_queries
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AmazonscrapeSpider(scrapy.Spider):
    name = "amazonScrape"
    allowed_domains = ["amazon.com"]
    BASE_URL = "https://www.amazon.com"
    KEYWORD_PRODUCT_URLS = set()
    PAGINATION = 21
    
    def start_requests(self):
        fake_requests = ['https://www.amazon.com', 'https://www.amazon.com/s?k=headsets', 'https://www.amazon.com/s?k=helmets', 'https://www.amazon.com/s?k=gadgets', 'https://www.amazon.com/s?k=rings', 'https://www.amazon.com/s?k=sheets']
        for fake_request in fake_requests:
            yield SeleniumRequest(
                url=fake_request, 
                callback=self.fetch_fake_request, 
                wait_time=10,
                wait_until=EC.visibility_of_element_located((By.XPATH, '//h1'))
            )
                
        keywords = read_queries('user_queries.json')
        for keyword in keywords:
            self.KEYWORD_PRODUCT_URLS = set()
            url = f"https://www.amazon.com/s?k={keyword}"
            
            yield SeleniumRequest(
                url=url, 
                callback=self.parse_pagination, 
                meta={'keyword': keyword},
                wait_time=10,
                wait_until=EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="puisg-row"]//h2/ancestor::div[@data-cy="title-recipe"]/a'))
            )
    
    def fetch_fake_request(self, response):
        print(response.xpath('normalize-space(//h1)').get())
        
    def parse_pagination(self, response):
        driver = response.meta['driver']
        time.sleep(random.choice([1.7, 2.1, 2.2]))
        response2 = scrapy.Selector(text=driver.page_source)
        
        product_elements = response2.xpath('//div[@class="puisg-row"]//h2/ancestor::div[@data-cy="title-recipe"]/a')
        for element in product_elements:
            url = element.xpath('./@href').get()
            if url and "sspa" not in url:
                if not url.startswith("http"):
                    url = f"{self.BASE_URL}{url}"
                
                if url not in self.KEYWORD_PRODUCT_URLS:
                    self.KEYWORD_PRODUCT_URLS.add(url)
                    self.log(f"Collected URL: {url}")
                    yield SeleniumRequest(
                        url=url,
                        callback=self.parse_product,
                        meta={'keyword': response.meta['keyword']},
                        wait_time=10,
                        wait_until=EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "a-button-thumbnail")]//img'))
                    )

        next_page = response.xpath('//a[contains(text(), "Next")]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            if f"page={self.PAGINATION}" not in next_page_url:
                yield SeleniumRequest(
                    url=next_page_url,
                    callback=self.parse_pagination,
                    meta={'keyword': response.meta['keyword']},
                    wait_time=10,
                    wait_until=EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="puisg-row"]//h2/ancestor::div[@data-cy="title-recipe"]/a'))
                )
            else:
                return
        else:
            return
                
    def parse_product(self, response):
        try:
            driver = response.meta['driver']
            __ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h2[contains(text(), "Product Description")]')))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", __)
        except:
            pass
        
        product = Product(
            url=response.url,
            name=self.product_name(response),
            price=self.product_price(response),
            options=self.product_options(response),
            specifications=self.product_specifications(response),
            features=self.product_features(response),
            breadcrumbs=self.product_breadcrumbs(response),
            web_series=self.product_weblink_series(response),
            media={
                'primary_image': self.product_primary_image(response),
                'secondary_images': self.product_secondary_images(response),
                'featured_images': self.product_featured_images(response),
                'videos': self.product_videos(response)
            },
            ratings={
                'avg_rating': self.product_avg_rating(response),
                'total_ratings': self.product_total_rating(response),
                'distribution': self.product_rating_dist(response)
            }
        )
        
        save_to_json(product.to_dict(), f"{response.meta['keyword']}.json")    
        yield product.to_dict()
    
    def product_name(self, response):
        name = response.xpath('normalize-space(//h1[@id="title"]/span)').get()
        return name
    
    def product_price(self, response):
        whole_price = response.xpath('normalize-space(//span[@class="a-price-whole"])').get()
        if whole_price:
            fraction = response.xpath('normalize-space(//span[@class="a-price-fraction"])').get()
            if fraction:
                return f'${whole_price}{fraction}'
        return ""
    
    def product_features(self, response):
        features = []
        feature_elements = response.xpath('//h1[contains(text(), "About this item")]/parent::div/ul/li')
        if feature_elements:
            for feature_element in feature_elements:
                text = feature_element.xpath('normalize-space(.)').get()
                features.append(text)
        return features
    
    def product_primary_image(self, response):
        img = response.xpath('//div[@id="imgTagWrapperId"]//img/@src').get()
        if img:
            return img.replace("X300", "X800").replace("Y300", "Y800")
        return ""
        
    def product_secondary_images(self, response):
        imgs = []
        img_elements = response.xpath('//span[contains(@class, "a-button-thumbnail")]//img')
        if len(img_elements) > 1:
            for img_element in img_elements[1:]:
                image = img_element.xpath('./@src').get()
                if 'm.media-amazon' in image:
                    imgs.append(image.replace("40_.jpg", "_.jpg"))
            return imgs
        return imgs
        
    def product_featured_images(self, response):
        imgs = []
        img_elements = response.xpath('//div[contains(@class, "background-image")]//img')
        if img_elements:
            for img_element in img_elements:
                image = img_element.xpath('./@src').get()
                if '.jpg' in image:
                    imgs.append(image)
        img_elements = response.xpath('//h2[contains(text(), "Product Description")]/parent::div//div[contains(@class, "aplus-module-wrapper")]/img')
        if img_elements:
            for img_element in img_elements:
                image = img_element.xpath('./@src').get()
                if '.jpg' in image:
                    imgs.append(image)
        return imgs
        
    def product_videos(self, response):
        video_links = response.xpath('//ol[@class="a-carousel"]//video/@src').getall()
        if video_links:
            return video_links
        return []
    
    def product_options(self, response):
        item = defaultdict(list)
        divs = response.xpath('//div[contains(@id, "inline-twister-row")]/@id').getall()
        if not divs:
            return {}
        keys = [key.split('_name')[0].split('-')[-1] for key in divs]
        for key in keys:
            xpath_prefix = f'//div[contains(@id, "expander-content-{key}")]'
            if key == 'color':
                type_elements = response.xpath(f'{xpath_prefix}//span[@class="a-list-item"]//img')
                item[key] = list(set(img.xpath('./@alt').get() for img in type_elements if img.xpath('./@alt').get()))
            else:
                type_elements = response.xpath(f'{xpath_prefix}//span[@class="a-list-item"]')
                item[key] = [elem.xpath('normalize-space(.)').get() for elem in type_elements if elem.xpath('normalize-space(.)').get()]
        return dict(item)
                    
    def product_specifications(self, response):
        keys = []
        values = []
        rows = response.xpath('//div[@class="a-section a-spacing-small a-spacing-top-small"]//tbody/tr')
        for row in rows:
            key = row.xpath("normalize-space(./td[1])").get()
            value = row.xpath("normalize-space(./td[2])").get()
            if key and value:
                keys.append(key)
                values.append(value)
        rows = response.xpath('//table[contains(@id, "productDetails")]//tbody/tr')
        for row in rows:
            key = row.xpath("normalize-space(./th)").get()
            value = row.xpath("normalize-space(./td)").get()
            if key and value:
                keys.append(key)
                values.append(value)
        if keys and values:
            return dict(zip(keys, values))
        return {}
    
    def product_avg_rating(self, response):
        rating = response.xpath('normalize-space(//span[@class="a-size-medium a-color-base"])').get()
        if rating:
            return rating
        return "-"
    
    def product_total_rating(self, response):
        rating = response.xpath('normalize-space(//span[@data-hook="total-review-count"])').get()
        if rating:
            return rating
        return "-"
    
    def product_rating_dist(self, response):
        ratings = response.xpath('//ul[contains(@class, "ratings-histogram")]/li/span/a/div[1]/text()').getall()
        percents = response.xpath('//ul[contains(@class, "ratings-histogram")]/li/span/a/div[3]/text()').getall()
        if ratings and percents:
            return dict(zip(ratings, percents))
        return {}
    
    def product_breadcrumbs(self, response):
        breadcrumbs = []
        breadcrumb_elements = response.xpath('//div[@data-cel-widget="wayfinding-breadcrumbs_feature_div"]//li//a')
        if not breadcrumb_elements:
            return breadcrumbs
        for breadcrumb_element in breadcrumb_elements:
            breadcrumbs.append(breadcrumb_element.xpath('normalize-space(.)').get())
        return breadcrumbs

    def product_weblink_series(self, response):
        breadcrumbs = []
        links = []
        breadcrumb_elements = response.xpath('//div[@data-cel-widget="wayfinding-breadcrumbs_feature_div"]//li//a')
        if not breadcrumb_elements:
            return {}
        for breadcrumb_element in breadcrumb_elements:
            breadcrumb_text = breadcrumb_element.xpath('normalize-space(.)').get()
            breadcrumb_link = breadcrumb_element.xpath('./@href').get()
            if breadcrumb_text and breadcrumb_link:
                full_link = breadcrumb_link if breadcrumb_link.startswith('http') else self.BASE_URL + breadcrumb_link
                breadcrumbs.append(breadcrumb_text)
                links.append(full_link)
        return dict(zip(breadcrumbs, links))
