# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy import log, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from lab_1.items import LabItem

class LabSpider(CrawlSpider):
	
	name = "LabSpider"
	allowed_domains = ["shzfcg.gov.cn"]
	start_urls = [
		"http://www.shzfcg.gov.cn:8090/new_web/cjxx/center_hz_zb.jsp",
	]
	link_extractor = {
    	'content' : SgmlLinkExtractor(allow = 'code=\d+&type=\d+$'),
    }
	page = 1
	
	def parse(self, response):
		count = 0
		
		for element in response.xpath('//td[@align="right"]/a').extract():
			if count > 0 :
				break
				
			element = element.encode('utf-8')
			pos = element.find('下一页')
			element = element.decode('utf-8')
			if pos > -1 :
				count = count+1
				LabSpider.page = LabSpider.page+1
				yield Request(url = '%s?page=%d' %(LabSpider.start_urls[0] , LabSpider.page), callback = self.parse)

		for link in self.link_extractor['content'].extract_links(response):
			yield Request(url = link.url, callback=self.parse_page_content)
			
	def parse_page_content(self, response):
		item = LabItem()

		tempstr = ''.join(response.xpath('//td[@class="text1"]/strong/text()').extract())
		if tempstr.find('---') > -1 :
			item['projName'] = tempstr[tempstr.find('---')+3:] 
		else :
			item['projName'] = tempstr[tempstr.find('--')+2:] 
		
		for element in response.xpath('//td[@class="text3"]/text()').extract():
			
			element = element.encode("utf-8")
			pos_1_1 = element.find('供应商：') # 成交供应商 和 中标供应商
			pos_1_2 = element.find('中标单位：')
			pos = element.find('：')
			
			pos_2_1 = element.find('采购日期')
			pos_2_2 = element.find('评审日期')
			pos_2_3 = element.find('评标日期')
			
			pos_3_1 = element.find('成交金额')
			pos_3_2 = element.find('中标金额')
			element = element.decode("utf-8")
			
			if pos_1_1 > -1 or pos_1_2 > -1 :
				#item['bug'] = element
				#item['pos'] = pos
				
				pos_1 = max(pos_1_1, pos_1_2)
				'''
				if element.find(',') > -1 :	
					item['merchant'] = element[pos/2:element.find(',')]
				#elif element.find('。') > -1 :
				#	tempstr = element[pos+2:elment.find('。')]
				else :
					item['merchant'] = element[pos/2:]
				'''
				if element.find(',') > -1 :	
					item['merchant'] = element[pos_1:element.find(',')]
				#elif element.find('。') > -1 :
				#	tempstr = element[pos+2:elment.find('。')]
				else :
					item['merchant'] = element[pos_1:]
				
			if pos_2_1 >=0 or pos_2_2 >=0 or pos_2_3 >=0 :
				item['date'] = re.compile('\d{4}\D\d+\D\d+').search(element).group()
				
			if pos_3_1 > -1 or pos_3_2 > -1 :
				item['price'] = re.compile('\d+\.?\d*').search(element).group()
			
		return item
		
