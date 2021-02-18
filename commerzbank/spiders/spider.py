import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CommerzbankItem
from itemloaders.processors import TakeFirst


class CommerzbankSpider(scrapy.Spider):
	name = 'commerzbank'
	start_urls = ['https://www.commerzbank.de/en/hauptnavigation/presse/pressemitteilungen/archiv1/2021/1__quartal_1/presse_archiv_21_01.html']

	def parse(self, response):
		year_links = response.xpath('//div[@class="navVert"]/ul/li[2]/ul/li/ul/li/a/@href').getall()
		yield from response.follow_all(year_links, self.parse_year)

	def parse_year(self, response):
		quarter_links = response.xpath('//div[@class="navVert"]/ul/li[2]/ul/li/ul/li/ul/li/a/@href').getall()
		yield from response.follow_all(quarter_links, self.parse_quarter)

	def parse_quarter(self, response):
		post_links = response.xpath('//a[@class="more"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//div[@id="contentBody"]/div[@class="section"]/h3/text()').get()
		description = response.xpath('//div[@id="contentBody"]/div[@class="section"]//text()[normalize-space() and not(ancestor::h3 | ancestor::a | ancestor::span[@class="fileinfo"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@id="contentBody"]/div[@class="section"]/p/text()').get()
		description = re.sub(date, '', description)

		item = ItemLoader(item=CommerzbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
