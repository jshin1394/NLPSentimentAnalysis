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

class SpiderH:

    def __init__(self, url):
        self.main = url
        self.domain = urlparse(self.main).hostname
        self.type = 'text/html'
        self.max = 150
        self.processed = defaultdict(list)
        self.stoplist_hash = set()
        self.wfile = open('HanPost.raw', 'w')
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
            # print(url)

            loop_count = 0
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

                    if 'home' in url:
                        html_list = soup.find_all('a', href = True)

                        for element in html_list:
                            html = element['href']
                            html_domain = urlparse(html).hostname
                            if self.main not in html:
                                if html.startswith('/arti/'):
                                    html = 'http://' + self.domain + html
                                    if self.main not in html and html not in url_list:
                                        url_list.append(html)
                                elif self.domain == html_domain and 'list' not in html and 'gallery' not in html \
                                    and ('international' in html or 'politics' in html or 'news' in html) and html not in url_list:
                                    url_list.append(html)
                            

                        url_list = self.sort_html(url_list)
                        # print('\n'.join(url_list))
                        # break;

                    else:
                        keywords = self.get_keyword(soup)
                        
                        if keywords:
                            self.processed[url] = keywords
                            count += 1
                            # print(keywords)
                            self.wfile = open('HanPost.raw', 'a')
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
                            if self.main not in html:
                                if html.startswith('/arti/'):
                                    html = 'http://' + self.domain + html
                                    if self.main not in html and html not in url_list:
                                        url_list.append(html)
                                elif self.domain == html_domain and 'list' not in html and 'gallery' not in html \
                                    and ('international' in html or 'politics' in html or 'news' in html) and html not in url_list:
                                    url_list.append(html)


                        # print('\n'.join(url_list))
                        url_list = self.sort_html(url_list)

        self.wfile.close()

    def sort_html(self, url_list):
        temp_list = list()
        for html in url_list:
            try:
                request = urlopen(html)
                if request.status == 200 and html not in self.processed:
                    if re.search('/\d{1,20}.html', html):
                        data = request.read().decode('utf-8')
                        if re.search('국제</a>', data):
                            if re.search('>미국', data):
                                temp_list.append((html,0))
                            else:
                                temp_list.append((html,2))
                        elif re.search('정치</a>', data):
                            temp_list.append((html, 1))
                    elif 'politics' in html:
                        temp_list.append((html, 2))

                    elif 'international' in html:
                        temp_list.append((html, 2))

                    else:
                        temp_list.append((html, 3))
            except:
                pass

        temp_list.sort(key=lambda x: x[1])
        temp_list = [x[0] for x in temp_list]

        return temp_list

    def get_keyword(self, soup):
        try:
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

            entire_text = [title " " + sub_title, text]

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