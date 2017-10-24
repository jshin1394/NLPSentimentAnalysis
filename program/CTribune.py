import re
import sys
import os
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict


DIR = "resource/"
stoplist = DIR + "common_words" 

class SpiderCT:

    def __init__(self, url):
        self.main = url
        self.domain = urlparse(self.main).hostname
        self.type = 'text/html'
        self.max = 200
        self.processed = defaultdict(list)
        self.stoplist_hash = set()
        self.wfile = open('Chicago.raw', 'w')
        self.wfile.close()

        self.initialize()
        self.search_url()

        
    def initialize(self):
        for line in open(stoplist, 'r'):
            if line:
                self.stoplist_hash.add(line.strip())

    def search_url(self):
        count = 0
        url_list = [self.main]

        while count < self.max and url_list:
            # print(url_list)
            url = url_list.pop(0)
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
                        break
                    pass

            if data:
                if self.type in data.headers.get('content-type'):
                    data = data.read()
                    soup = BeautifulSoup(data, 'html.parser')

                    keywords = self.get_keyword(soup)
                    if keywords:
                        self.processed[url] = keywords
                        count += 1
                        # print(keywords)
                        self.wfile = open('Chicago.raw', 'a')
                        self.wfile.write('.I ' + str(count) + '\n')
                        self.wfile.write('.U\n')
                        self.wfile.write(url + '\n')
                        self.wfile.write('.T\n')
                        self.wfile.write(keywords[0] + '\n')
                        self.wfile.write('.B\n')
                        self.wfile.write(keywords[1] + '\n')
                        self.wfile.close()


                    #parse html with domain and non self referencing
                    html_list = soup.find_all('a', href = True)
                    for element in html_list:
                        html = element['href']
                        html_domain = urlparse(html).hostname
                        if html.startswith('/news/') or html.startswith('/topic/'):
                            html = 'http://' + self.domain + html
                            if self.main not in html and html not in url_list:
                                url_list.append(html)
                        elif self.main not in html and html_domain == self.domain and html not in url_list:
                            url_list.append(html)
                    
                    url_list = self.sort_html(url_list)
                    # print ('\n'.join(url_list))

        self.wfile.close()

    def sort_html(self, url_list):
        temp_list = list()

        for html in url_list:
            try:
                request = urlopen(html)
                if request.status == 200 and html not in self.processed:
                    data = request.read().decode('utf-8')
                    if 'news/nationworld/politics/' in html:
                        if 'html' in html:
                            temp_list.append((html, 0))
                        else:
                            temp_list.append((html, 2))
                    elif re.search('>National politics', data) and 'html' in html:
                        temp_list.append((html, 1))
                    elif 'politic' in html:
                        if 'html' in html:
                            temp_list.append((html, 1))
                        else:
                            temp_list.append((html, 2))
                    elif 'business' in html or 'international' in html:
                        if 'html' in html:
                            temp_list.append((html, 2))
                        else:
                            temp_list.append((html, 3))
                    else:
                        temp_list.append((html, 4))
            except:
                pass

        temp_list.sort(key=lambda x: x[1])
        temp_list = [x[0] for x in temp_list]

        return temp_list

    def get_keyword(self, soup):
        try:
#            import pdb;
#            pdb.set_trace()
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
