import scrapy
import requests
import re
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from .utils import phoneNumberPattern, getFax, getPhone, getAddress

import requests

geojsonData = requests.get('https://data.sfgov.org/api/geospatial/8nkz-x4ny?method=export&format=GeoJSON').json()

def getFeature(district):
  hits = [j for j in geojsonData['features'] if j['properties']['supervisor'] == district]
  if hits:
    return hits[0]
  return None

class SFSpider(CrawlSpider):
    name = 'sf'
    start_urls = [
        'https://sfbos.org/roster-members'
    ]
    allowed_domains = ['sfbos.org']
    
    rules = (
        Rule(LinkExtractor(allow=('-district-')), callback='parse_item'),
    )

    def parse_item(self, response):
        info = {}

        for a in response.css('a::attr(href)').extract():
            if 'mailto:' in a:
                info['email'] = a.split(':')[1]

        #             e><div id="sup_right">
        # <div class="sup_name"><a href="/sites/default/files/yee.jpg" title="High Resolution Photo of Supervisor Yee"><img alt="Norman Yee District7 landing imge" class="sup_img" src="/modules/showimage.aspx?imageid=5869" style="margin: 100px 10px 10px; width: 195px; height: 264px; float: right;" /></a>Norman Yee</div>

        # <div class="sup_district">District 7</div>


        info['name'] = response.css('.sup_name ::text').extract()[0]
        info['body'] = 'SF Board of Supervisors'

        district = response.css('.sup_district ::text').extract()[0].split(' ')[1]
        info['district'] = district

        info['geojson'] = getFeature(district)
  
        contactInfo = response.xpath("//*[contains(text(), 'Contact Info')]/following::p").extract()[0].replace('<br>', '').replace('<p>', '').replace('</p>', '')
        print ('xp:' + contactInfo)
        lines = contactInfo.split('\n')
        addressLines = []
        for l in lines:
          addressLines.append(l.strip())
          if ', Ca' in l or ', CA' in l:
            break
        
        info['addresses'] = [
            {
              'address': getAddress(addressLines),
              'phones': getPhone(lines),
              'fax': getFax(lines),
          }
        ]
        info['office'] = {
            'level': 'locality',
            'role': 'legislatorUpperBody',
            'name': 'Board of Supervisors Member'
        }


        yield info