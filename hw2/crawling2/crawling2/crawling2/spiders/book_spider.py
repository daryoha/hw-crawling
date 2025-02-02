import scrapy
from ..items import BookItem

class ChitaiGorodSpider(scrapy.Spider):
    name = 'chitai_gorod'
    allowed_domains = ['chitai-gorod.ru']
    start_urls = ['https://www.chitai-gorod.ru/catalog/books-18030?page=1']

    def parse(self, response):
        book_links = response.xpath('//a[@class="product-card__title"]/@href').getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        if "page" in response.url:
            current_page = int(response.url.split("page=")[-1])
        else:
            current_page = 1
        next_page = f"https://www.chitai-gorod.ru/catalog/books-18030?page={current_page + 1}"
        print("ogoi", next_page)

        yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_book(self, response):
        item = BookItem()

        def safe_strip(value):
            return value.strip() if value else None

        item['title'] = safe_strip(response.xpath('//h1[@class="detail-product__header-title"]/text()').get())
        item['author'] = safe_strip(response.xpath('//a[@class="product-info-authors__author"]/text()').get())
        item['description'] = safe_strip(response.xpath('//article[@class="detail-description__text"]/text()').get())
        item['price_amount'] = safe_strip(response.xpath('//span[contains(@class, "product-offer-price__current")]/text()').re_first(r'\d+'))
        item['price_currency'] = safe_strip(response.xpath('//meta[@itemprop="priceCurrency"]/@content').get())
        item['rating_value'] = safe_strip(response.xpath('//meta[@itemprop="ratingValue"]/@content').get())
        item['rating_count'] = safe_strip(response.xpath('//meta[@itemprop="ratingCount"]/@content').get())
        item['publication_year'] = safe_strip(response.xpath('//span[@itemprop="datePublished"]/text()').get())
        item['isbn'] = safe_strip(response.xpath('//span[@itemprop="isbn"]/text()').get())
        item['pages_cnt'] = safe_strip(response.xpath('//span[@itemprop="numberOfPages"]/text()').get())
        item['publisher'] = safe_strip(response.xpath('//span[@itemprop="publisher"]/text()').get())
        item['book_cover'] = safe_strip(response.xpath('//img[@class="product-info-gallery__poster"]/@src').get())
        item['source_url'] = safe_strip(response.url)

        yield item