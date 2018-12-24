# -*- coding: utf-8 -*-
import datetime
import re
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

    name = 'dailymail'
    allowed_domains = ['dailymail.co.uk']
    base_url = 'https://www.dailymail.co.uk/home/search.html?size=50&sel=site&searchPhrase=EU%20Referendum&sort=recent&channel=news&type=article&days=all&offset='
    offset = 3850
    size = 50
    start_urls = [base_url + str(offset)]


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('string(//div[contains(@class,"heading-tag-switch")]/h2[1])').extract_first().replace('\n', '')
        brexit_news['title'] = title
        text = ''
        for sel in response.xpath('//div[contains(@itemprop,"articleBody")]//p'):
            line = sel.xpath('string(.)').extract_first()
            if line is not None:
                text += line + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = 'dailymail'
        date = response.xpath('string(//span[contains(@class,"article-timestamp-published")])').extract_first()
        date = date.split(',')[-1].strip().split()
        date = date[2] + '-' + str(month_of_year.index(date[1]) + 1) + '-' + re.sub('\D', '', date[0])
        brexit_news['date'] = date
        # print(brexit_news)
        if check_date(brexit_news['date']):
            yield brexit_news


    def parse(self, response):

        for sel in response.xpath('//div[@class="sch-res-content"]/h2/a'):
            article_url = parse.urljoin(response.url, sel.xpath('@href').extract_first())
            if check_url(article_url):
                yield Request(article_url, self.article)

        # handle every page
        self.offset += self.size
        next_page_url = self.base_url + str(self.offset)
        if self.offset <= 4200:
            yield Request(next_page_url, self.parse)
