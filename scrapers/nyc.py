import scrapy
import requests


def extractContactInfo(contactInfoEl):
    lines = [
        l.replace('\r\n', '') for l in contactInfoEl.css('p ::text').getall()
    ]
    return {
        'phone': lines[2].split(' ')[0],
        'fax': lines[3].split(' ')[0],
        'address_line1': lines[0],
        'address_city': lines[1].split(',')[0].strip(),
        'address_state': lines[1].split(',')[1].strip(),
        'address_zip': lines[1].split(' ')[2].strip()
    }

def getMetaValueByName(response, attr):
    return response.css(f'meta[name="{attr}"]::attr(content)').extract()[0]

def getMetaValueByProperty(response, attr):
    return response.css(f'meta[property="{attr}"]::attr(content)').extract()[0]

class NYCSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = [f'https://council.nyc.gov/district-{num}/' for num in range(0,70)]

    def parse(self, response):
        for contactInfo in response.css(
                'div[aria-label="District office contact information"]'):
            yield {'district_office': extractContactInfo(contactInfo)}

        for contactInfo in response.css(
                'div[aria-label="Legislative office contact information"]'):
            yield {'legislative_office': extractContactInfo(contactInfo)}

        for a in response.css('.callout a::attr(href)').extract():
            if 'mailto:' in a:
                yield {'email': a.split(':')}

        yield {'twitter': getMetaValueByName(response, "twitter:creator")}
        yield {'image': getMetaValueByProperty(response, "og:image")}
        yield {'name': getMetaValueByProperty(response, "og:site_name")}

        district = getMetaValueByProperty(response, "og:title").split(' ')[1]
        yield {'district': district}

        r = requests.get(
            f'https://nyc-council.carto.com/api/v2/sql?q=SELECT%20*%20FROM%20nyc_city_council_dist_cm%20WHERE%20dist%3D{district}&format=geojson'
        )
        yield {'geojson': r.json()}