# -*- coding: utf-8 -*-
import datetime
from urllib import parse

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

    name = 'express'
    allowed_domains = ['express.co.uk']
    start_urls = ['https://www.express.co.uk/search?s=brexit&order=oldest&o=2570']


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
        brexit_news['media'] = 'express'
        brexit_news['date'] = response.xpath('//meta[@itemprop="datepublished"]/@content').extract_first()[:10]
        # print(brexit_news)
        yield brexit_news


    def parse(self, response):

        for sel in response.xpath('//a[contains(@class,"result-item")]'):
            article_url = parse.urljoin(response.url, sel.xpath('@href').extract_first())
            date = sel.xpath('//time/@datetime').extract_first()[:10]
            if check_url(article_url) and check_date(date):
                yield Request(article_url, self.article)

        # handle every page
        next_page_url = parse.urljoin(response.url, response.xpath('//a[@class="loadMore"]/@href').extract_first())
        params = parse.urlparse(next_page_url)[4].split('&')
        params = [i for i in params if i.startswith('o=')][0]
        num = int(params[2:])
        if num <= 3020:
            yield Request(next_page_url, self.parse)
