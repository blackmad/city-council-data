from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import subprocess
import tempfile
import json
import os

setting = get_project_settings()
process = CrawlerProcess(setting)

for spider_name in process.spider_loader.list():
    f = tempfile.NamedTemporaryFile(delete=False)
    tempFilename = f.name + '.json'
    print ("Running spider %s" % (spider_name))
    setting['FEED_URI'] = tempFilename
    process2 = CrawlerProcess(setting)
    process2.crawl(spider_name)
    process2.start() # the script will block here until the crawling is finished

    print(tempFilename)

    lines = ', '.join([l for l in open(tempFilename)])
    data = json.loads('{"members": [' + lines + ']}')
    json.dump(data, open(f'data/{spider_name}.json', 'w'))



