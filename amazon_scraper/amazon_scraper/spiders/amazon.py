from scrapy import Spider, Request
from ..items import AmazonProductItem
import random
import time

class AmazonSpider(Spider):
    name = 'amazon'
    allowed_domains = ['amazon.in']
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENTS': [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54"
        ]
    }

    def __init__(self, keyword=None, num_products=30, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.num_products = int(num_products)
        self.products_count = 0
        self.start_urls = [f'https://www.amazon.in/s?k={keyword.replace(" ", "+")}']

    def get_random_headers(self):
        return {
            "User-Agent": random.choice(self.custom_settings['USER_AGENTS']),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                headers=self.get_random_headers(),
                callback=self.parse,
                dont_filter=True
            )

    def parse(self, response):
        products = response.xpath('//div[@data-component-type="s-search-result"]')
        
        for product in products:
            if self.products_count >= self.num_products:
                return
                
            item = AmazonProductItem()
            
            item['rank'] = self.products_count + 1
            item['asin'] = product.xpath('@data-asin').get()
            item['title'] = product.xpath('.//h2[contains(@class, "a-size-mini")]//text()').get('').strip()
            
            price = product.xpath('.//span[@class="a-price-whole"]/text()').get()
            if not price:
                price = product.xpath('.//span[@class="a-color-base"]/text()').get()
            item['price'] = price.strip() if price else "N/A"
            
            item['link'] = f"https://www.amazon.in/dp/{item['asin']}" if item['asin'] else "N/A"
            
            rating = product.xpath('.//span[@class="a-icon-alt"]/text()').get()
            item['rating'] = rating.split()[0] if rating else "N/A"
            
            reviews = product.xpath('.//span[@class="a-size-base s-underline-text"]/text()').get()
            item['reviews'] = reviews.strip('() ') if reviews else "N/A"
            
            bought_count = "N/A"
            bought_text = product.xpath('.//span[contains(@class, "a-size-small social-proofing-faceout-title-text")]/text()').get()
            if not bought_text:
                bought_text = product.xpath('.//span[@class="a-size-base a-color-secondary"]/text()').get()
            if bought_text and "bought in past month" in bought_text.lower():
                bought_count = bought_text.split()[0]
            item['bought_last_month'] = bought_count
            
            item['type'] = "Sponsored" if "AdHolder" in product.xpath('@class').get('') else "Organic"
            
            self.products_count += 1
            yield item

        # Handle pagination
        if self.products_count < self.num_products:
            next_page = response.xpath('//a[@class="s-pagination-next"]/@href').get()
            if next_page:
                yield Request(
                    url=f"https://www.amazon.in{next_page}",
                    headers=self.get_random_headers(),
                    callback=self.parse,
                    dont_filter=True
                )