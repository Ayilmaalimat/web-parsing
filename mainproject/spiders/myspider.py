import scrapy
import csv
import json
from mainproject.items import mains
from scrapy.pipelines.images import ImagesPipeline


class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://agro.gov.kg/']
    page_incr = 1
    pagination_url = 'https://agro.gov.kg/wp-admin/admin-ajax.php'
    parse_url = []

    def parse(self, response):
        links = ['https://agro.gov.kg/language/ru/ministry/deputy-ministers/']
        links2 = ['https://agro.gov.kg/language/ru/ministry/minister/']
        sections = response.xpath(
            '//a[@class="modsection__link"]/@href').extract()
        main = ['https://agro.gov.kg/']
        star_urls = ['https://agro.gov.kg/']

        for link in star_urls:
            yield scrapy.Request(url=link, callback=self.pagparse)

        for link in links:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.nextparse)

        for link in links2:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parseministr)

        for link in sections:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.sectionparse)

        for link in main:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.mainparse)

    def sectionparse(self, response):
        item = mains()
        item['title'] = response.xpath(
            '//p[@class="bfd-download-title"]/strong/text()').extract()
        item['text'] = response.css(
            '.bfd-bottom-zero small::text').extract()
        item['file_urls'] = self.url_join(response.xpath(
            '//a[@class="bfd-svg-container bfd-single-download-btn"]/@href').extract(), response)

        return item

    def postparse(self, response):
        item = mains()
        item['title'] = response.xpath(
            '//h1[@class="post-title entry-title"]/text()').get()
        item['date'] = response.xpath(
            '//span[@class="date meta-item"]/span/text()').get()
        item['text'] = response.xpath(
            '//div[@class="entry-content entry clearfix"]/p/text()').getall()
        item['image_urls'] = self.url_join(response.xpath(
            '//figure[@class="single-featured-image"]/img/@data-src').extract(), response)

        return item

    def pagparse(self, response):
        sel = scrapy.selector.Selector(response)

        if self.page_incr > 1:
            data_json = json.loads(json.loads(response.body))
            sel = scrapy.selector.Selector(text=data_json['code'])

        links = sel.xpath('//a[@class="more-link button"]/@href').extract()
        self.parse_url += links

        if response.css("h3"):
            self.page_incr += 1
            formdata = {
                "action": "tie_blocks_load_more",
                "block[cat][]": [
                    "16",
                    "1"
                ],
                "block[id][]": "1",
                "block[number]": "5",
                "block[pagi]": "load-more",
                "block[excerpt]": "true",
                "block[excerpt_length]": "15",
                "block[post_meta]": "true",
                "block[read_more]": "true",
                "block[breaking_effect]": "reveal",
                "block[sub_style]": "timeline",
                "block[style]": "timeline",
                "page": str(self.page_incr),
                "width": "single"
            }
            yield scrapy.http.FormRequest(url=self.pagination_url, formdata=formdata, callback=self.pagparse)
        else:
            for link in self.parse_url:
                url = response.urljoin(link)
                yield scrapy.Request(url=url, callback=self.postparse)

    def parseministr(self, response):
        item = mains()
        item['title'] = response.xpath(
            '//div[@class="elementor-text-editor elementor-clearfix"]/h2/text()').get()
        item['text'] = response.css('.elementor-tab-content p::text').extract()
        item['image_urls'] = self.url_join(response.xpath(
            '//div[@class="elementor-image"]/img/@data-src').extract(), response)

        return item

    def nextparse(self, response):
        item = mains()
        item['title'] = response.xpath(
            '//h2[@class="elementor-heading-title elementor-size-default"]/span/text()').extract()
        item['text'] = response.css('.elementor-tab-content p::text').extract()
        item['image_urls'] = self.url_join(response.xpath(
            '//figure[@class="wp-caption"]/img/@data-src').extract(), response)

        return item

    def mainparse(self, response):
        item = mains()
        item['title'] = response.css('.main-menu ul li a::text').extract()
        item['text'] = response.css(
            '.main-menu ul li a::attr("href")').extract()

        return item

    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls
