# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os


class BrexitnewsPipeline(object):

    base_dir = 'spider_news'

    def process_item(self, item, spider):
        if item['title'] is not None and item['media'] is not None:
            filename = os.path.join(os.path.dirname(os.path.abspath('.')), self.base_dir, item['media'], str(hash(item['title'])))
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(item['title'])
                f.write('\n\n')
                f.write(item['date'])
                f.write('\n\n')
                f.write(item['text'])
        return item
