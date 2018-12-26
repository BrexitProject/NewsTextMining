# -*- coding: utf-8 -*-
import datetime

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

    name = 'dailystar'
    allowed_domains = ['dailystar.co.uk']
    base_url = 'https://www.dailystar.co.uk/search?q=brexit&section=131&o='
    page = 3150
    start_urls = ['https://www.dailystar.co.uk/search?q=brexit&section=131&o=' + str(page)]


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('string(//h1[contains(@itemprop,"headline")])').extract_first().strip()
        brexit_news['title'] = title
        text = ''
        for sel in response.xpath('//div[contains(@data-type,"article-body")]//p'):
            line = sel.xpath('string(.)').extract_first()
            if line is not None:
                text += line + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = 'dailystar'
        brexit_news['date'] = response.xpath('//time[@datetime]/@datetime').extract_first()[:10]
        # print(brexit_news)
        if check_date(brexit_news['date']):
            yield brexit_news


    def parse(self, response):

        for sel in response.xpath('//a[contains(@class,"result-item")]'):
            article_url = sel.xpath('@href').extract_first()
            if check_url(article_url):
                yield Request(article_url, self.article)

        # handle every page
        self.page += 10
        next_page_url = self.base_url + str(self.page)
        if self.page <= 3260:
            yield Request(next_page_url, self.parse)
