# TODO
# - email address
# - photos
# - url

import scrapy
import requests
import re
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json

from .utils import phoneNumberPattern, getFax, getPhone, getAddress, strip_tags, getLinesUntilPhone

import requests

geojsonData = requests.get('https://services2.arcgis.com/1OML3Q9DZatjcY7Q/arcgis/rest/services/Council_Dist_Transparent/FeatureServer/0/query?f=geojson&where=1=1&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=*&maxRecordCountFactor=4&outSR=4326&resultOffset=0&resultRecordCount=4000&cacheHint=true&quantizationParameters={%22mode%22:%22view%22,%22originPosition%22:%22upperLeft%22,%22tolerance%22:1000.0583354500041176,%22extent%22:{%22xmin%22:40.74,%22ymin%22:-74,%22xmax%22:40.74,%22ymax%22:-75,%22spatialReference%22:{%22wkid%22:4326,%22latestWkid%22:4326}}}').json()
from shapely.geometry import mapping, shape
from shapely.ops import unary_union


shapes = [shape(j['geometry']) for j in geojsonData['features'] ]
unionedShape = unary_union(shapes)

def getFeature(district):
  hits = [j for j in geojsonData['features'] if j['properties']['DISTRICT'] == district]
  if hits:
    return hits[0]
  return None

class PhillySpider(CrawlSpider):
    name = 'philly'
    start_urls = [
        'http://phlcouncil.com/council-members/'
    ]

    def parse(self, response):
        info = {}

        for card in response.css('.x-card-outer'):
          info['name'] = card.css('.x-face-title ::text').extract()[0]

          districtPattern = re.compile('DISTRICT (\d+)')
          match = districtPattern.search(card.css('.x-face-outer.front .x-face-text').extract()[0])
          info['office'] = {
            'level': 'locality',
            'role': 'legislatorUpperBody',
          }

          info['body'] = 'Philadelphia City Council'

          if match:
            district = match.groups()[0]
            info['geojson'] = getFeature(district)
            info['district'] = district
            info['office']['name'] = 'District Council Member'
          else:
            info['geojson'] = mapping(unionedShape)
            # info['district'] = 'At-Large'
            info['office']['name'] = 'Council Member At-Large'
        
          info['url'] = 'http://phlcouncil.com' + card.css('.x-face-outer.back a::attr(href)').extract()[0]

          contactInfo = strip_tags(card.css('.x-face-outer.back .x-face-text').extract()[0])
          
          info['addresses'] = [
              {
                'address': getAddress(getLinesUntilPhone(contactInfo)),
                'phone': getPhone(contactInfo),
                'fax': getFax(contactInfo),
            }
          ]

          yield info