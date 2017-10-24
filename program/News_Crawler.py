import re
import sys
import os
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict
from CTribune import SpiderCT
from WTPost import SpiderWT
from HanPost import SpiderH



DIR = "resource/"
stoplist = DIR + "common_words" 

if __name__ == '__main__':
#    url = sys.argv[1] 
    url = 'http://www.chicagotribune.com/news/nationworld/politics/ct-trump-shift-on-nafta-20170427-story.html'
    #url = 'http://www.washingtontimes.com/news/2017/apr/27/white-house-trump-made-right-call-firing-flynn/'
    #url = 'http://www.hani.co.kr/arti/international/america/792525.html'
    domain = urlparse(url).hostname

    if 'chicagotribune' in domain:
        cralwer = SpiderCT(url)
    elif 'hani' in domain:
        crawler = SpiderH(url)
    elif 'washingtontimes' in domain:
        crawler = SpiderWT(url)
    # crawler = Spider('https://www.washingtonpost.com/business/economy/trump-to-unveil-proposal-for-massive-tax-cut/2017/04/26/2097fe42-2a94-11e7-be51-b3fc6ff7faee_story.html?hpid=hp_hp-top-table-main_trumptax-140pm%3Ahomepage%2Fstory&utm_term=.42a4c36f2b43')

