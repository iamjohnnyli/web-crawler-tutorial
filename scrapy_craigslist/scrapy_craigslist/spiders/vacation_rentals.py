# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re


class VacationRentalsSpider(scrapy.Spider):
    name = 'vacation_rentals'
    allowed_domains = ['craigslist.org']
    start_urls = ['http://seattle.craigslist.org/d/vacation‐rentals/search/vac/']

    def parse(self, response):
        # Extract all wrapper for each list item between <p class="result-info"></p>
        vacs = response.xpath('//p[@class="result-info"]')
        # Get next page button URL <a href="/search/vac?s=120" class="button next" title="next page">next &gt; </a>
        next_rel_url = response.xpath('//a[@class="button next"]/@href').extract_first()
        # Get full address.
        next_url = response.urljoin(next_rel_url)
        # Go through all the pages.
        yield Request(next_url, callback=self.parse)

        # Loop each item to extract title, posted date, rental price, number of bedrooms, and neighborhood
        for vac in vacs:
            # Get title from <a></a> tag.
            title = vac.xpath('a/text()').extract_first()
            # Get posted date from <time class="result-date" datetime="2019-03-06 18:34" title="Wed 06 Mar 06:34:28 PM">Mar  6</time> block. Use @datetime for attribute datetime.
            pdate = vac.xpath('time/@datetime').extract_first().split()[0]
            # Get rental price form <span class="result-price">$84</span>
            rprice = vac.xpath('span/span[@class="result-price"]/text()').extract_first()
            # Get Number of bedrooms from <span class="housing">2br - 760ft<sup>2</sup> - </span> and clean up the extra
            nbedroom = str(vac.xpath('span/span[@class="housing"]/text()').extract_first()).split('-')[0].strip()
            # Get Neighborhood from <span class="result-hood"> (*** - *****)</span>
            hood = re.sub('[()]', '', str(vac.xpath('span/span[@class="result-hood"]/text()').extract_first())).strip()
            # Get the address of description page of each vacation house.
            vacaddress = vac.xpath('a/@href').extract_first()
            # We needed open the URL of each house and scrape the house description, while passing the meta to parse_page function.
            yield Request(vacaddress, callback=self.parse_page, meta={'URL': vacaddress, 'Title': title, 'Posted Date':pdate,"Rental Price":rprice,"Number of bedrooms":nbedroom, "Neighborhood":hood})

    # Extract description page of the vacation house.
    def parse_page(self, response):
        # Pass the variables
        url = response.meta.get('URL')
        title = response.meta.get('Title')
        pdate = response.meta.get('Posted Date')
        rprice = response.meta.get('Rental Price')
        nbedroom = response.meta.get('Number of bedrooms')
        hood = response.meta.get('Neighborhood')
        # Get the description.
        description = "".join(line for line in response.xpath('//*[@id="postingbody"]/text()').extract())

        yield{'Title': title, 'Posted Date':pdate,"Rental Price":rprice,"Number of bedrooms":nbedroom, "Neighborhood":hood,'Description':description}
