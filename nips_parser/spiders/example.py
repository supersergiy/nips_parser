# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider

OUTPUT_FILE_PATH = './2017_nips.csv'
class NipsSpider(scrapy.Spider):
    name = "nips"
    def __init__(self, *args):
        super(NipsSpider, self).__init__()
        self.output_file = open(OUTPUT_FILE_PATH, mode='w')
        self.output_file.write('Year,Name,Event Type,PDF Link,' +
                               'NIPS Link,Abstract,Bibtex Link,Authors' +
                               '\n')
    def write_paper(self, paper_dict):
        values = [paper_dict['year'], paper_dict['name'], paper_dict['event_type'],
                  paper_dict['pdf_link'], paper_dict['nips_link'], paper_dict['abstract'],
                  paper_dict['bibtex_link'], paper_dict['authors']]
        clean_values = [v.replace(',', ';') for v in values]
        clean_values = [v.replace('\n', '   ') for v in clean_values]
        csv_entry = ','.join(clean_values) + '\n'
        try:
            self.output_file.write(csv_entry.encode('ascii', 'replace'))
        except Exception as e:
            self.log('ERROR: {}'.format(e))
            raise CloseSpider('Paper write error occured')

    def start_requests(self):
        urls = [
            'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-30-2017',
            'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-29-2016',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
	heading = response.css('title::text')[0].extract()
        if heading.endswith('Proceedings'):
            self.log('Parsing the head page')
            for item in response.css('li')[1:]:
                paper_suffix = item.css('a::attr(href)').extract()[0]
                paper_link   = response.urljoin(paper_suffix)
                self.log('Found paper! {}'.format(paper_link))
                yield response.follow(paper_link, callback=self.parse)
        else:
            self.log('Parsing a paper page')
            paper_dict = {}
            paper_dict['name'] = heading
            paper_dict['year'] = response.css('a::text')[2].extract()
            pdf_link_suffix = response.css('a::attr(href)')[4].extract()
            paper_dict['pdf_link'] = response.urljoin(pdf_link_suffix)
            paper_dict['nips_link'] = response._url
            bibtex_link_suffix = response.css('a::attr(href)')[5].extract()
            paper_dict['bibtex_link'] = response.urljoin(bibtex_link_suffix)
            event_string = response.css('h3::text').extract()[1]
            skip_count   = len('Conference Event Type: ')
            event_type   = event_string[skip_count:]
            paper_dict['event_type'] = event_type
            author_list = response.css('li.author a::text').extract()
            paper_dict['authors']  = '; '.join(author_list)
            paper_dict['abstract'] = response.css('p::text').extract()[1]
            self.write_paper(paper_dict)

        '''page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)'''
