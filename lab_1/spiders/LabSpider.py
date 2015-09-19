# -*- coding: utf-8 -*-

import scrapy
from scrapy import log, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
#from scrapy.contrib.exporter import JsonLinesItemExporter

from lab_1.items import LabItem

class LabSpider(CrawlSpider):
	
	name = "LabSpider"
	allowed_domains = ["shzfcg.gov.cn"]
	start_urls = [
		"http://www.shzfcg.gov.cn:8090/new_web/cjxx/center_hz_zb.jsp",
	]
	link_extractor = {
    	'page_down' : SgmlLinkExtractor(allow = ''),
    	'content' : SgmlLinkExtractor(allow = 'code=\d+&type=\d+$'),
					#SgmlLinkExtractor(allow = '/bbscon,board,\w+,file,M\.\d+\.A\.html$'),
    }
	
	def parse(self, response):
		for link in self.link_extractor['content'].extract_links(response):
			yield Request(url = link.url, callback=self.parse_page_content)
			
	def parse_page_content(self, response):
		item = LabItem()
		log.msg("just for debug!!!", level=log.DEBUG)
		item['url'] = response.url
		tempstr = ''.join(response.xpath('//td[@class="text1"]/strong/text()').extract())
		item['projName'] = tempstr[tempstr.find('---')+3:] 
		
		for element in response.xpath('//td[@class="text3"]/text()').extract():
			
			element = element.encode("utf-8")
			pos_1 = element.find('供应商') # 成交供应商 和 中标供应商
			pos_2_1 = element.find('采购日期')
			pos_2_2 = element.find('评审日期')
			pos_2_3 = element.find('评标日期')
			pos_3_1 = element.find('成交金额')
			pos_3_2 = element.find('中标金额')
			element = element.decode("utf-8")
			#log.msg("pos = %d element = %s " % (pos,'') , level=log.INFO)
			
			if pos_1 > -1 :
				log.msg("just for debug", level=log.DEBUG)
				item['merchant'] = element[6:element.find(',')]
			
			if pos_2_1 >=0 or pos_2_2 >=0 or pos_2_3 >=0 :
				item['date'] = element[element.find(':')+2:]
				
			if pos_3_1 > -1 or pos_3_2 > -1 :
				pos = max(pos_3_1, pos_3_2)
				item['price'] = element[pos+5:-1]
			
		return item
		
