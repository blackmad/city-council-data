import scrapy
import requests
import re
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from .utils import phoneNumberPattern, getFax, getPhone, getAddress

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

        info['district'] = response.css('.sup_district ::text').extract()[0].split(' ')[1]

  
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
              'phone': getPhone(lines),
              'fax': getFax(lines),
          }
        ]

        # # info['channels'] = {}
        # # info['twitter'] = getMetaValueByName(response, "twitter:creator")
        # info['photoUrl'] = getMetaValueByProperty(response, "og:image")
        # info['name'] = getMetaValueByProperty(response, "og:site_name")
        # info['urls'] = [ getMetaValueByProperty(response, "og:url") ]
        # info['body'] = "New York City Council"

        # info['office'] = {
        #     'level': 'locality',
        #     'role': 'legislatorUpperBody',
        #     'name': 'City Council Member'
        # }

        # district = getMetaValueByProperty(response, "og:title").split(' ')[1]
        # info['district'] = district

        # r = requests.get(
        #     f'https://nyc-council.carto.com/api/v2/sql?q=SELECT%20*%20FROM%20nyc_city_council_dist_cm%20WHERE%20dist%3D{district}&format=geojson'
        # )
        # info['geojson'] = r.json()

        yield info