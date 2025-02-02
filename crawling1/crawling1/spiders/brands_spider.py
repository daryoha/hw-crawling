import scrapy
from ..items import MerchantItem

class MerchantSpider(scrapy.Spider):
    name = "merchant_spider"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands"]
    def parse(self, response):
        rows = response.xpath('/html/body/section/div/div[2]/div/div[1]/div/table/tbody/tr')
        for row in rows:
            brand_link = row.xpath('./td[2]/a/@href').get()

            if brand_link:
                yield response.follow("https://merchantpoint.ru" + brand_link, callback=self.parse_brand)

        next_page = response.xpath('/html/body/section/div/div[2]/div/div[3]/ul/li/a[contains(text(), "Вперед")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_brand(self, response):
        org_name = response.xpath('/html/body/section/div/div[1]/div/div/h1/text()').get()
        org_description = response.xpath('/html/body/section/div/div[3]/div[1]/div/div/div[1]/div/div[2]/div/p[2]/text()').get()
        rows = response.xpath('/html/body/section/div/div[3]/div[3]/div/div/div[1]/div[1]/div/div/table/tbody/tr')

        for row in rows:
            point_link = row.xpath('./td[2]/a/@href').get()
            print("aaa")
            if point_link:
                yield response.follow(point_link,
                                    callback=self.parse_point,
                                    meta={'org_name': org_name,
                                            'org_description': org_description})
        
    def parse_point(self, response):
        merchant_name = response.xpath('/html/body/section/div/div[3]/div[1]/div/div/div[1]/div/div[2]/p[2]/text()').get()
        mcc = response.xpath('/html/body/section/div/div[3]/div[1]/div/div/div[1]/div/div[2]/p[4]/a/text()').get()
        address = response.xpath('/html/body/section/div/div[3]/div[1]/div/div/div[1]/div/div[2]/p[7]/text()').get()
        geo_coordinates = response.xpath('/html/body/section/div/div[3]/div[1]/div/div/div[1]/div/div[2]/p[8]/text()').get()

        item = MerchantItem()


        item['merchant_name'] = (merchant_name or '').strip()
        item['mcc'] = (mcc or '').strip()
        item['address'] = (address or '').strip()
        item['geo_coordinates'] = (geo_coordinates or '').strip()
        item['org_name'] = (response.meta['org_name'] or '').strip()
        item['org_description'] = (response.meta['org_description'] or '').strip()
        item['source_url'] = response.url

        print(item)

        yield item