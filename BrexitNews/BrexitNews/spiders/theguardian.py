# -*- coding: utf-8 -*-
import datetime

import scrapy
from scrapy import Request

from BrexitNews.items import BrexitNewsItem

start_date = datetime.date(2016, 6, 16)
end_date = datetime.date(2016, 6, 22)
month_of_year = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']


def check_date(response):
    year = int(response.xpath('//span[@class="fc-today__year"]/text()').extract_first())
    month = month_of_year.index(response.xpath('//span[@class="fc-today__month"]/text()').extract_first()) + 1
    day = int(response.xpath('//span[@class="fc-today__dayofmonth js-dayofmonth"]/text()').extract_first())
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

    name = 'theguardian'
    allowed_domains = ['theguardian.com']
    start_urls = ['https://www.theguardian.com/politics/eu-referendum/2016/jun/16/all']


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('//h1[contains(@class,"content__headline")]/text()').extract_first().replace('\n', '')
        brexit_news['title'] = title
        text = ''
        # for sel in response.xpath('//div[contains(@class,"content__article-body")]//p'):
        for sel in response.xpath('//p'):
            line = sel.xpath('text()').extract_first()
            if line is not None:
                text += line + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = 'theguardian'
        brexit_news['date'] = response.xpath('//time[contains(@itemprop,"datePublished")]/@datetime').extract_first()[:10]
        # print(text)
        yield brexit_news


    def parse(self, response):
        # check date
        if not check_date(response):
            return

        for sel in response.xpath('//*[@id="top"]/div[4]/div/section/div/div[2]/div[@class="fc-slice-wrapper"]//a[@aria-hidden="true"]'):
            article_url = sel.xpath('@href').extract_first()
            if 'video' not in article_url:
                yield Request(article_url, self.article)

        # handle every page
        next_page_url = response.xpath('//*[@id="top"]/div[4]/div/section/div/div[2]/div[last()]/a[last()]/@href').extract_first()
        if check_url(next_page_url):
            yield Request(next_page_url, self.parse)
