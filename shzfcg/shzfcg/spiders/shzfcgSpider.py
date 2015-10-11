# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy import log, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from shzfcg.items import ShzfcgItem

class shzfcgSpider(CrawlSpider):
	
	name = "shzfcgSpider"
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
				shzfcgSpider.page = shzfcgSpider.page+1
				yield Request(url = '%s?page=%d' %(shzfcgSpider.start_urls[0] , shzfcgSpider.page), callback = self.parse)

		for link in self.link_extractor['content'].extract_links(response):
			yield Request(url = link.url, callback=self.parse_page_content)
			
	def parse_page_content(self, response):
		item = ShzfcgItem()

		tempstr = ''.join(response.xpath('//td[@class="text1"]/strong/text()').extract())
		if tempstr.find('---') > -1 :
			item['projName'] = tempstr[tempstr.find('---')+3:] 
		else :
			item['projName'] = tempstr[tempstr.find('--')+2:] 
		
		for element in response.xpath('//td[@class="text3"]/text()').extract():
			
			element = element.encode("utf-8")

			pos_1_1 = element.find('供应商：') # 成交供应商 和 中标供应商
			pos_1_2 = element.find('中标单位：')
			
			pos_2_1 = element.find('采购日期')
			pos_2_2 = element.find('评审日期')
			pos_2_3 = element.find('评标日期')
			pos_2_4 = element.find('成交日期')
			
			pos_3_1 = element.find('成交金额')
			pos_3_2 = element.find('中标金额')
			pos_3_3 = element.find('成交价格')
			pos_3_4 = element.find('合价')
			pos_3_5 = element.find('采购成交价')
			pos_3_6 = element.find('中标价')
			
			#element = element.decode("utf-8")
			
			if pos_1_1 > -1 or pos_1_2 > -1 :
				#'''
				start = max(element.find(':'),element.find('：'))
				end = max(element.find(','),element.find('，'))
				#end = max(end, element.find('、'))
				end = max(end, element.find('；'))
				#end = max(end, element.find('。'))
				#end = max(end, element.find(' '))
				temp_str = element[start+3 : end]
				item['merchant'] = temp_str.decode('utf-8')
				'''
				pos_1 = max(pos_1_1, pos_1_2)
				
				if element.find(',') > -1 :	
					item['merchant'] = element[pos_1:element.find(',')]
				
				else :
					item['merchant'] = element[pos_1:]
				'''
				
			element = element.decode("utf-8")
			
			if pos_2_1 >=0 or pos_2_2 >=0 or pos_2_3 >=0 or pos_2_4 >=0 :
				item['date'] = re.compile('\d{4}\D\d+\D\d+').search(element).group()
				
			if pos_3_1 > -1 or pos_3_2 > -1 or pos_3_3 > -1 or pos_3_4 > -1 or pos_3_5 > -1 or pos_3_6 > -1 :
				'''
				start1 = max(pos_3_1, pos_3_2)
				start2 = max(pos_3_3, pos_3_4)
				start3 = max(pos_3_5, pos_3_6)
				start4 = max(start1, start2)
				start = max(start3, start4)
				 
				element.encode("utf-8")
				temp_str1 = element[start:-1]
				temp_str = temp_str1.decode("utf-8")
				element = element.decode("utf-8")
				'''
				oldPrice = re.compile('\d+\,?\d+\,?\d+\.?\d*').search(element).group()
				p = re.compile("\d+,\d+?")
				for com in p.finditer(oldPrice):
					mm = com.group()
					oldPrice = oldPrice.replace(mm, mm.replace(",",""))
				oldPrice = oldPrice.encode('utf-8')
				item['price'] = float(oldPrice)

		if item["projName"].find(u"失败公告") == -1 :	
			return item
