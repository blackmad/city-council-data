import scrapy
import requests
import re
import logging

from .utils import phoneNumberPattern, getFax, getPhone, getAddress

def extractContractInfoFromLines(lines):
    phoneLines = [l for l in lines if phoneNumberPattern.search(l)]

    # some addresses have BONUS info after so we need to filter that out
    # [{'lines': ['456 5th Ave', 'Brooklyn, NY 11215', '718-499-1090 phone', '718-499-1997 fax', '', 'The office is ADA-accessible. There is an elevator at the end of the entrance hallway behind the stairs.', '']}]
    possibleAddressLines = [
        l for l in lines if not phoneNumberPattern.search(l) and l
    ]
    addressLines = []
    for l in possibleAddressLines:
        addressLines.append(l)
        if ', NY' in l:
            break

    return {
        'address': getAddress(addressLines),
        'phone': getPhone(phoneLines),
        'fax': getFax(phoneLines)
    }


def extractContactInfo(contactInfoEl, defaultName):
    lines = [
        l.replace('\r\n', '').strip()
        for l in contactInfoEl.css('p ::text').getall()
    ]

    addresses = []
    currentAddress = {'name': defaultName}
    logging.warning('extractContactInfo')
    for index, line in enumerate(lines):
        if 'Office:' in line:
            if index != 0:
                addresses.append(currentAddress)
            currentAddress = {}
            currentAddress['name'] = line.replace(':', '').strip()
            currentAddress['lines'] = []
        else:
            if 'lines' not in currentAddress:
                currentAddress['lines'] = []
            currentAddress['lines'].append(line)
    addresses.append(currentAddress)
    logging.debug('addresses %s' % addresses)

    return [{
        **extractContractInfoFromLines(address['lines']),
        'name':
        address['name'] or defaultName,
    } for address in addresses]


def getMetaValueByName(response, attr):
    return response.css(f'meta[name="{attr}"]::attr(content)').extract()[0]


def getMetaValueByProperty(response, attr):
    return response.css(f'meta[property="{attr}"]::attr(content)').extract()[0]


class NYCSpider(scrapy.Spider):
    name = 'nyc'
    start_urls = [
        f'https://council.nyc.gov/district-{num}/' for num in range(0, 70)
    ]

    def parse(self, response):
        info = {}

        offices = []
        for contactInfo in response.css(
                'div[aria-label="District office contact information"]'):
            offices = offices + extractContactInfo(contactInfo,
                                                   'District Office')

        for contactInfo in response.css(
                'div[aria-label="Legislative office contact information"]'):
            offices = offices + extractContactInfo(contactInfo,
                                                   'Legislative Office')

        info['addresses'] = offices

        for a in response.css('.callout a::attr(href)').extract():
            if 'mailto:' in a:
                info['email'] = a.split(':')[1]

        # info['channels'] = {}
        # info['twitter'] = getMetaValueByName(response, "twitter:creator")
        info['photoUrl'] = getMetaValueByProperty(response, "og:image")
        info['name'] = getMetaValueByProperty(response, "og:site_name")
        info['urls'] = [ getMetaValueByProperty(response, "og:url") ]
        info['body'] = "New York City Council"

        info['office'] = {
            'level': 'locality',
            'role': 'legislatorUpperBody',
            'name': 'City Council Member'
        }

        district = getMetaValueByProperty(response, "og:title").split(' ')[1]
        info['district'] = district

        r = requests.get(
            f'https://nyc-council.carto.com/api/v2/sql?q=SELECT%20*%20FROM%20nyc_city_council_dist_cm%20WHERE%20dist%3D{district}&format=geojson'
        )
        info['geojson'] = r.json()

        yield info