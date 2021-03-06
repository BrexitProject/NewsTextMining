# -*- coding: utf-8 -*-
import datetime
import re

import scrapy
from scrapy import Request

from BrexitNews.items import BrexitNewsItem

start_date = datetime.date(2016, 6, 16)
end_date = datetime.date(2016, 6, 24)
month_of_year = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']


def check_date(param):
    param = param.split('-')
    year = int(param[0])
    month = int(param[1])
    day = int(param[2])
    date = datetime.date(year, month, day)
    if start_date <= date <= end_date:
        return True
    return False


def check_url(url):
    if url is not None:
        url = url.strip()
        if url != '' and url != 'None':
            return True
    return False


class TheguardianSpider(scrapy.Spider):

    name = 'inews'
    allowed_domains = ['inews.co.uk']
    start_urls = ['https://inews.co.uk/page/662/?s=brexit']


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('string(//h1[contains(@class,"entry-title")])').extract_first().strip()
        brexit_news['title'] = title
        text = ''
        for sel in response.xpath('//div[contains(@itemprop,"articleBody")]//p'):
            line = sel.xpath('string(.)').extract_first()
            if line is not None:
                text += line.strip() + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = self.name
        brexit_news['date'] = response.xpath('//time[contains(@itemprop,"datePublished")]/@datetime').extract_first()[:10]
        # print(brexit_news)
        if check_date(brexit_news['date']):
            yield brexit_news


    def parse(self, response):

        date = response.xpath('//span[@class="teaser-topic__pubdate"]/text()')[-1].extract()
        date = date.strip().split()
        date = date[2] + '-' + str(month_of_year.index(date[0]) + 1) + '-' + re.sub('\D', '', date[1])
        if not check_date(date):
            return

        for sel in response.xpath('//a[contains(@class,"teaser-topic__link-primary")]'):
            article_url = sel.xpath('@href').extract_first()
            if check_url(article_url):
                yield Request(article_url, self.article)

        # handle every page
        next_page_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if check_url(next_page_url):
            yield Request(next_page_url, self.parse)
