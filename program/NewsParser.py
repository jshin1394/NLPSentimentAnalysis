import re
import sys
import os
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict, OrderedDict


DIR = "resource/"
stoplist = DIR + "common_words" 

class NParser:

    def __init__(self, url, stoplist_hash, positive_hash, negative_hash,\
                incrementer_hash, decrementer_hash, inverter):
        self.url = url
        self.domain = urlparse(self.url).hostname
        self.type = 'text/html'
        self.stoplist_hash = stoplist_hash
        self.positive_hash = positive_hash
        self.negative_hash = negative_hash
        self.incrementer_hash = incrementer_hash
        self.decrementer_hash = decrementer_hash
        self.inverter = inverter
        self.check_input()



    def check_input(self):
        if self.domain is None:
            raise ValueError

        if 'chicago' not in self.domain and 'washingtonpost' not in self.domain\
        and 'hani' not in self.domain:
            raise ValueError

        

    def search_url(self):
        url = self.url
        if url.startswith('//'):
            url = url.replace('//','')
#            print(url)

        loop_count = 0
        data = None
        while True:
            try:
                data = urlopen(url)
                if data.status == 200:
                    break;
            except urllib.error.HTTPError as err:
                loop_count += 1
                if loop_count > 5:
                    raise ValueError
                pass

        if data:
            if self.type in data.headers.get('content-type'):
                data = data.read()
                soup = BeautifulSoup(data, 'html.parser')

                related_text = self.related_text(soup)
                if related_text:
                    title = related_text[0]
                    body = related_text[1]
                    keywords = self.keywords(title + ' ' + body)
                    sentiment = self.sentiment_analysis(title + ' ' + body)
                    return (title, keywords, sentiment)

    def related_text(self, soup):
        try:
            title = ''
            sub_title = ''
            text = ''
            if 'chicagotribune' in self.domain:
                title_text = soup.find('h1', {'itemprop':'headline'})
                title = title_text.get_text()

                body_text = soup.findAll('div', {'class':'trb_ar_page', 'data-role':'pagination_page'})
                text = []
                for body in body_text:
                    ps = body.findAll('p')
                    for p in ps:
                        paragraph = p.get_text().strip()
                        if paragraph:
                            text.append(paragraph)
                text = ' '.join(text)

            elif 'washingtontimes' in self.domain:
                title_text = soup.find('h1', attrs={'class' : 'page-headline'})
                title = title_text.get_text()

                body_text = soup.find('div', attrs={'class' : 'article-text'}).findAll('p')
                text = []
                for p in body_text:
                    paragraph = p.get_text().strip()
                    if paragraph:
                        text.append(paragraph)
                text = ' '.join(text)
            
            elif 'hani' in self.domain:
                title_text = soup.find('span', attrs={'class' : 'title'})
                sub_title_text = soup.find('div', attrs={'class' : 'subtitle'})

                title = title_text.get_text()
                sub_title = sub_title_text.get_text()

                body_text = soup.find('div', {'class' : 'text'})
                text = []
                for element in body_text:
                    element = str(element)
                    if not re.match('^<', element):
                        if element:
                            text.append(element.strip())

                text = ' '.join(text)
                title = title + ' ' + sub_title
            
            
            entire_text = [title, text]
            return entire_text
            # text_keyws = list(self.keywords(text).keys())
            # title_keyws = list(self.keywords(title).keys())
            # return list(set(text_keyws + title_keyws))
        except:
            return []


    def keywords(self, text):
        NUM_KEYWORDS = 10
        text = self.split_words(text)
        # of words before removing blacklist words
        if text:
            num_words = len(text)
            text = [x for x in text if x not in self.stoplist_hash]
            freq = {}
            for word in text:
                if word in freq:
                    freq[word] += 1
                else:
                    freq[word] = 1

            min_size = min(NUM_KEYWORDS, len(freq))
            keywords = sorted(freq.items(),
                              key=lambda x: (x[1], x[0]),
                              reverse=True)
            keywords = keywords[:min_size]
            keywords = dict((x, y) for x, y in keywords)

            for k in keywords:
                articleScore = keywords[k] * 1.0 / max(num_words, 1)
                keywords[k] = articleScore * 1.5 + 1
            return dict(keywords)
        else:
            return dict()

    def split_words(self, text):
        try:
            text = re.sub(r'[^\w ]', '', text)  # strip special chars
            return [x.strip('.').lower() for x in text.split()]
        except TypeError:
            return None

    def sentiment_analysis(self, text):
        text = self.split_words(text)
        vec1 = OrderedDict()
        for t in text:
            val = vec1.get(t, 0)
            vec1[t] = val + 1
        prev = ''
        sentiment_score = 0
        for t in vec1:
            if t in self.positive_hash:
                if prev in self.incrementer_hash:
                    sentiment_score += self.positive_hash[t] * self.incrementer_hash[prev]
                elif prev in self.decrementer_hash:
                    sentiment_score += self.positive_hash[t] * self.decrementer_hash[prev]
                elif prev in self.inverter:
                    sentiment_score += self.positive_hash[t] * -1
                else:
                    sentiment_score += self.positive_hash[t]
            elif t in self.negative_hash:
                if prev in self.incrementer_hash:
                    sentiment_score += self.negative_hash[t] * self.incrementer_hash[prev]
                elif prev in self.decrementer_hash:
                    sentiment_score += self.negative_hash[t] * self.decrementer_hash[prev]
                elif prev in self.inverter:
                    sentiment_score += self.negative_hash[t] * -1
                else:
                    sentiment_score += self.negative_hash[t]

        if sentiment_score < 50 and sentiment_score >= 0:
            return 'Neutral~Positive'
        elif sentiment_score > 50:
            return 'Positive'
        elif sentiment_score < 0 and sentiment_score > -50:
            return 'Negative~Neutral'
        else:
            return 'Negative'