''' -*- coding: utf-8 -*-
'''

import scrapy
import re
from scrapy import log, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from shzfcg.items import ShzfcgItem

class shzfcgSpider(CrawlSpider):
    '''
    This shzfcgSpider is used for extracting certain links and html text,
    from wich it can obtain relevant attributes.
    '''

    name = "shzfcgSpider"
    allowed_domains = ["shzfcg.gov.cn"]
    start_urls = [
        "http://www.shzfcg.gov.cn:8090/new_web/cjxx/center_hz_zb.jsp",
    ]
    link_extractor = {
        'content' : SgmlLinkExtractor(allow=r'code=\d+&type=\d+$'),
    }
    page = 1

    def parse(self, response):
        '''
        this function is used to find the url of the next page and recursion.
        '''

        count = 0

        for element in response.xpath('//td[@align="right"]/a').extract():
            if count > 0:
                break

            element = element.encode('utf-8')
            pos = element.find('下一页')
            element = element.decode('utf-8')
            if pos > -1:
                count = count+1
                shzfcgSpider.page = shzfcgSpider.page+1
                yield Request(url = '%s?page=%d' % (shzfcgSpider.start_urls[0],shzfcgSpider.page), callback= self.parse)

        for link in self.link_extractor['content'].extract_links(response):
            yield Request(url= link.url, callback= self.parse_page_content)

    def parse_page_content(self, response):
        '''
        this function is used to specify the attributes.
        '''
        item = ShzfcgItem()

        tempstr = ''.join(response.xpath('//td[@class="text1"]/strong/text()').extract())
        if tempstr.find('---') > -1:
            item['projName'] = tempstr[tempstr.find('---')+3:] 
        else:
            item['projName'] = tempstr[tempstr.find('--')+2:] 

        for element in response.xpath('//td[@class="text3"]/text()').extract():

            pos_1_1 = element.find(u"供应商：") # 成交供应商 和 中标供应商
            pos_1_2 = element.find(u"中标单位：")
            pos_1_3 = element.find(u"中标人：")

            pos_2_1 = element.find(u"采购日期")
            pos_2_2 = element.find(u"评审日期")
            pos_2_3 = element.find(u"评标日期")
            pos_2_4 = element.find(u"成交日期")

            pos_3_1 = element.find(u"成交金额")
            pos_3_2 = element.find(u"中标金额")
            pos_3_3 = element.find(u"成交价格")
            pos_3_4 = element.find(u"合价")
            pos_3_5 = element.find(u"采购成交价")
            pos_3_6 = element.find(u"中标价")

            if pos_1_1 > -1 or pos_1_2 > -1 or pos_1_3 > -1:

                start = max(pos_1_1, pos_1_2)
                start = max(start, pos_1_3)
                temp_element = element[start:]

                start = max(temp_element.find(u":"),temp_element.find(u"："))
                flag1 = temp_element.find(u",")
                flag2 = temp_element.find(u"，")
                flag3 = temp_element.find(u"；")
                flag4 = temp_element.find(u" ", 12)
                flag5 = temp_element.find(u"。")
                end = max(flag1, flag2, flag3, flag4, flag5)
                if flag1 > -1 and flag1 < end:
                    end = flag1
                if flag2 > -1 and flag2 < end:
                    end = flag2
                if flag3 > -1 and flag3 < end:
                    end = flag3
                if flag4 > -1 and flag4 < end:
                    end = flag4
                if flag5 > -1 and flag5 < end:
                    end = flag5

                if temp_element.find(u": ") > -1 or temp_element.find(u"： ") > -1:
                    temp_str = temp_element[start+2 : end]
                elif temp_element.find(u"：") > -1:
                    temp_str = temp_element[start+1 : end]
                else :
                    temp_str = temp_element[start : end]

                item['merchant'] = temp_str

            if pos_2_1 >=0 or pos_2_2 >=0 or pos_2_3 >=0 or pos_2_4 >=0:
                item['date'] = re.compile(r'\d{4}\D\d+\D\d+').search(element).group()

            if pos_3_1 > -1 or pos_3_2 > -1 or pos_3_3 > -1 or pos_3_4 > -1 or pos_3_5 > -1 or pos_3_6 > -1:

                start1 = max(pos_3_1, pos_3_2)
                start2 = max(pos_3_3, pos_3_4)
                start3 = max(pos_3_5, pos_3_6)
                start4 = max(start1, start2)
                start = max(start3, start4)

                temp_str = element[start:]
                end = temp_str.find(u"万")

                oldPrice = re.compile(r'\d+\,?\d+\,?\d+\.?\d*').search(temp_str).group()
                p = re.compile(r"\d+,\d+?")
                for com in p.finditer(oldPrice):
                    mm = com.group()
                    oldPrice = oldPrice.replace(mm, mm.replace("," , ""))
                oldPrice = oldPrice.encode('utf-8')
                item['price'] = float(oldPrice)
                if end > -1:
                    item['price'] = item['price']*10000

        if item["projName"].find(u"失败公告") == -1:	
            return item
