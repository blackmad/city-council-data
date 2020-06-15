from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import subprocess
import tempfile
import json
import os
from multiprocessing import Process

setting = get_project_settings()
process = CrawlerProcess(setting)


def reprocessFile(file, outputRoot):
    members = [json.loads(l) for l in open(file)]

    features = []

    for member in members:
        if 'geojson' not in member:
            continue
        geojson = member['geojson']
        del member['geojson']

        feature = geojson
        if geojson['type'] == 'FeatureCollection':
            feature = geojson['features'][0]
        if 'coordinates' in geojson:
            feature = {'type': 'Feature', 'geometry': geojson}

        feature['properties'] = member

        features.append(feature)

    # data = json.loads('{"members": [' + lines + ']}')
    json.dump({'members': members},
              open(f'data/{outputRoot}.json', 'w'),
              sort_keys=True,
              indent=4)

    if features:
        json.dump({
            "type": "FeatureCollection",
            "features": features
        },
                  open(f'data/{outputRoot}.geojson', 'w'),
                  sort_keys=True,
                  indent=4)


def execute_crawling(spider_name, tempFilename):
    setting = get_project_settings()
    setting['FEED_URI'] = tempFilename
    process2 = CrawlerProcess(setting)
    process2.crawl(spider_name)
    process2.start(
    )  # the script will block here until the crawling is finished


def runSpiders():
    for spider_name in process.spider_loader.list():
        f = tempfile.NamedTemporaryFile(delete=False)
        tempFilename = f.name + '.json'
        print("Running spider %s" % (spider_name))

        p = Process(target=execute_crawling, args=(spider_name, tempFilename))
        p.start()
        p.join()  # this blocks until the process terminates
        print(tempFilename)

        reprocessFile(tempFilename, spider_name)


if __name__ == '__main__':
    runSpiders()

