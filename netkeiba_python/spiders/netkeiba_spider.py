import re

import scrapy


# この日付けより後のデータのみ取得する
DATA_MIN = '20071231'
# JSON のキー
KEYS = ['order',
        'frame',
        'number',
        'name',
        'age',
        'weight',
        'jocky',
        'time',
        'difference',
        'time-metric',
        'passed',
        'last-spurt',
        'odds',
        'popularity',
        'horse-weight',
        'train-time',
        'comments',
        'remarks',
        'trainer',
        'owner',
        'prise']


class NetkeibaSpider(scrapy.Spider):
    name = "netkeiba"
    start_urls = [
        'http://db.netkeiba.com/?pid=race_top',
    ]

    def parse(self, response):
        for day in response.css('.race_calendar td a::attr(href)'):
            full_url = response.urljoin(day.extract())

            yield scrapy.Request(full_url, callback=self.parse_race_list)

        next_page = response.css('.race_calendar li.rev a::attr(href)')

        if len(next_page) > 1:
            next_page = next_page[1].extract()
            m = re.search(r"date=([0-9]+)", next_page)

            if not m:
                return

            date = m.group(1)

            if next_page is not None and date > DATA_MIN:
                next_page = response.urljoin(next_page)

                yield scrapy.Request(next_page, callback=self.parse)

    def parse_race_list(self, response):
        for race in response.css('.race_top_data_info > dd > a::attr(href)'):
            full_url = response.urljoin(race.extract())

            yield scrapy.Request(full_url, callback=self.parse_race)

    def parse_race(self, response):
        if len(response.css('.race_table_01 tr')) < 2:
            return

        result = {'title': None,
                  'horses': [],
                  'diary': None,
                  'smalltxt': None}

        if response.css('title::text'):
            result['title'] = response.css('title::text').extract_first()

        if response.css('diary_snap_cut span::text'):
            result['diary'] = response.css('diary_snap_cut span::text').extract_first()

        if response.css('p.smalltxt::text'):
            result['smalltxt'] = response.css('p.smalltxt::text').extract_first()

        for i, tr in enumerate(response.css('.race_table_01 tr')[1:]):
            result['horses'].append({})

            for h, td in zip(KEYS, tr.css('td')):
                result['horses'][i][h] = None

                if td.css('::text'):
                    text = td.css('::text').extract()
                    text = ' '.join([t.strip() for t in text]).lstrip().rstrip()
                    result['horses'][i][h] = text

        yield result

