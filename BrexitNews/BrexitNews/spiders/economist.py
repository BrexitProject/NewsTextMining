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

    name = 'economist'
    allowed_domains = ['economist.com', 'google.com']
    start_urls = ['https://www.google.com/search?q=brexit+site:economist.com&tbas=0&tbs=cdr:1,cd_min:6/16/2016,cd_max:6/24/2016&start=0']


    def article(self, response):
        brexit_news = BrexitNewsItem()
        title = response.xpath('string(//h1[@class="flytitle-and-title__body"]/span[last()])').extract_first().strip()
        brexit_news['title'] = title
        text = ''
        for sel in response.xpath('//div[contains(@class,"blog-post__text")]//p'):
            line = sel.xpath('string(.)').extract_first()
            if line is not None:
                text += line.strip() + '\n\n'
        brexit_news['text'] = text
        brexit_news['url'] = response.url
        brexit_news['media'] = self.name
        brexit_news['date'] = response.xpath('//time[@itemprop="dateCreated"]/@datetime').extract_first()[:10]
        # print(brexit_news)
        yield brexit_news


    def parse(self, response):

        for sel in response.xpath('//div[@class="r"]/a[1]'):
            article_url = parse.urljoin(response.url, sel.xpath('@href').extract_first())
            if check_url(article_url):
                yield Request(article_url, self.article)

        # handle every page
        next_page_url = parse.urljoin(response.url, response.xpath('//a[@id="pnnext"]/@href').extract_first())
        if check_url(next_page_url):
            yield Request(next_page_url, self.parse)
