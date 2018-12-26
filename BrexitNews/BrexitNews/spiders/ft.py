# -*- coding: utf-8 -*-
import datetime
from urllib import parse

import scrapy
from scrapy import Request

from BrexitNews.items import BrexitNewsItem


def check_url(url):
    if url is not None:
        url = url.strip()
        if url != '' and url != 'None':
            return True
    return False


class TheguardianSpider(scrapy.Spider):

    name = 'ft'
    allowed_domains = ['www.ft.com']
    start_urls = ['https://www.ft.com/search?q=brexit&dateTo=2016-06-24&dateFrom=2016-06-16&sort=date']
    cookies = {

    }


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('string(//h1[@data-trackable="header"])').extract_first().strip()
        brexit_news['title'] = title
        text = ''
        for sel in response.xpath('//div[contains(@class,"article__content-body")]//p'):
            line = sel.xpath('string(.)').extract_first()
            if line is not None:
                text += line + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = 'ft'
        brexit_news['date'] = response.xpath('//time[contains(@class,"article-info__timestamp")]/@datetime').extract_first()[:10]
        # print(brexit_news)
        yield brexit_news


    def parse(self, response):

        for sel in response.xpath('//li[@class="search-results__list-item"]//a[@data-trackable="heading-link"]'):
            article_url = parse.urljoin(response.url, sel.xpath('@href').extract_first())
            if check_url(article_url) and 'video' not in article_url:
                yield Request(article_url, self.article, cookies=self.cookies)

        # handle every page
        next_page_url = parse.urljoin(response.url, response.xpath('//a[@data-trackable="next-page"]/@href').extract_first())
        if check_url(next_page_url):
            yield Request(next_page_url, self.parse, cookies=self.cookies)
