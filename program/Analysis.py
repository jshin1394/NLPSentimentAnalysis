import re
import sys
import os
import subprocess
import math
import operator
from nltk.stem import *
from PyDictionary import PyDictionary
from collections import defaultdict
from NewsParser import NParser


DIR = "./resource"
RDIR = "./result"

POSITIVE = DIR + "/positive.txt"
NEGATIVE = DIR + "/negative.txt"
INCREMENT = DIR + "/incrementer.txt"
DECREMENTER = DIR + "/decrementer.txt"
INVERTER = DIR + "/inverter.txt"
STOPLIST = DIR + "/common_words"

CTITLE = RDIR + "/Chicago.titles"
WTITLE = RDIR + "/WashingtonTimes.titles"
HTITLE = RDIR + "/HanPost.titles"

CURL = RDIR + "/Chicago.url"
WURL = RDIR + "/WashingtonTimes.url"
HURL = RDIR + "/HanPost.url"

CKEYS = RDIR + "/Chicago.key"
WKEYS = RDIR + "/WashingtonTimes.key"
HKEYS = RDIR + "/HanPost.stemmed.translated.key"

positive_hash = defaultdict(int)
negative_hash = defaultdict(int)
incrementer_hash = defaultdict(float)
decrementer_hash = defaultdict(float)
inverter = list()
stoplist_hash = set()

CHICAGO = RDIR + "/Chicago.stemmed"
WASHINGTON = RDIR + "/WashingtonTimes.stemmed"
# HAN = RDIR + "/HanPost.stemmed"
HAN = RDIR + "/HanPost.stemmed.translated"

#-----------------------------------------------#
CSENTIMENT = RDIR + "/Chicago.sentiment"
WSENTIMENT = RDIR + "/WashingtonTimes.sentiment"
HSENTIMENT = RDIR + "/HanPost.stemmed.translated.sentiment"

chicago_sentiment = []
washington_sentiment = []
han_sentiment = []
#-----------------------------------------------#

####################
#DOCUMENT VECTOR####
chicago_vector = []
washington_vector = []
han_vector = []


####################
#TITLES VECTOR####
chicago_titles = []
washington_titles = []
han_titles = []
####################

####################
#URL VECTOR####
chicago_urls = []
washington_urls = []
han_urls = []
####################


print("INITALIZING VECTORS")

###########
#READ DATA#
###########

for line in open(STOPLIST, 'r'):
    if line:
        stoplist_hash.add(line.strip())

for line in open(POSITIVE, 'r'):
    if line:
        positive_hash[line.strip()] = 1

for line in open(NEGATIVE, 'r'):
    if line:
        negative_hash[line.strip()] = -1

for line in open(INCREMENT, 'r'):
    if line:
        incrementer_hash[line.strip()] = 2

for line in open(DECREMENTER, 'r'):
    if line:
        incrementer_hash[line.strip()] = 0.5

for line in open(INVERTER, 'r'):
    if line:
        inverter.append(line.strip())

#########################################
#TITLE
chicago_titles.append('')
washington_titles.append('')
han_titles.append('')

for line in open(CTITLE, 'r'):
    if line:
        chicago_titles.append(line.strip())

for line in open(WTITLE, 'r'):
    if line:
        washington_titles.append(line.strip())

for line in open(HTITLE, 'r'):
    if line:
        han_titles.append(line.strip())

#########################################

#########################################
#URL
chicago_urls.append('')
washington_urls.append('')
han_urls.append('')

for line in open(CURL, 'r'):
    if line:
        chicago_urls.append(line.strip())

for line in open(WURL, 'r'):
    if line:
        washington_urls.append(line.strip())

for line in open(HURL, 'r'):
    if line:
        han_urls.append(line.strip())

#########################################

#########################################
#SENTIMENT
chicago_sentiment.append('')
for line in open(CSENTIMENT, 'r'):
    if line:
        chicago_sentiment.append(line.strip())

washington_sentiment.append('')
for line in open(WSENTIMENT, 'r'):
    if line:
        washington_sentiment.append(line.strip())

han_sentiment.append('')
for line in open(HSENTIMENT, 'r'):
    if line:
        han_sentiment.append(line.strip())

#########################################


total_chicago = 0
###################################
chicago_vector.append(defaultdict(int))

for word in open(CHICAGO, 'r'):
    word = word.strip()
    if not word or word == ".I 0":
        continue  # Skip empty line

    if word[:2] == ".I":
        new_doc_vec = defaultdict(int)
        chicago_vector.append(new_doc_vec)
        total_chicago += 1
    elif word not in stoplist_hash and re.search('[a-zA-Z]', word):
        new_doc_vec[word] += 1
###################################

total_washington = 0
###################################
washington_vector.append(defaultdict(int))

for word in open(WASHINGTON, 'r'):
    word = word.strip()
    if not word or word == ".I 0":
        continue  # Skip empty line

    if word[:2] == ".I":
        new_doc_vec = defaultdict(int)
        washington_vector.append(new_doc_vec)
        total_washington += 1
    elif word not in stoplist_hash and re.search('[a-zA-Z]', word):
        new_doc_vec[word] += 1
###################################

total_han = 0
# ###################################
han_vector.append(defaultdict(int))

for word in open(HAN, 'r'):
    word = word.strip()
    if not word or word == ".I 0":
        continue  # Skip empty line

    if word[:2] == ".I":
        new_doc_vec = defaultdict(int)
        han_vector.append(new_doc_vec)
        total_han += 1
    elif word[0] == '/':
        word_list = re.split('[/ ]', word.strip())
        for element in word_list:
            if element not in stoplist_hash and re.search('[0-9a-zA-Z]', element):
                new_doc_vec[element] += 1
# ###################################


class Newspaper:

    def __init__(self):
        self.chicago_vector = chicago_vector
        self.washington_vector = washington_vector
        self.han_vector = han_vector
        #total document
        ####################
        self.chicago_key_vector = []
        self.washington_key_vector = []
        self.han_key_vector = []
        self.initialize_vec()
        ####################
        self.total_chicago = total_chicago
        self.total_washington = total_washington
        self.total_han = total_han
        #title vector
        self.chicago_titles = chicago_titles
        self.washington_titles = washington_titles
        self.han_titles = han_titles
        #urls
        self.chicago_urls = chicago_urls
        self.washington_urls = washington_urls
        self.han_urls = han_urls
        #sentiments
        self.chicago_sentiment = chicago_sentiment
        self.washington_sentiment = washington_sentiment
        self.han_sentiment = han_sentiment

        self.stemmer = SnowballStemmer("english")
        self.stoplist_hash = stoplist_hash
        
        self.dictionary = PyDictionary()
        # self.stemmer = PorterStemmer()
        

    def menu(self):
        menu = "============================================================\n"\
        "==      Welcome to the Newspaper IR Engine       \n"\
        "==                                                          \n"\
        "==      Domains: {0}   {1}   {2}                                \n"\
        "==      Total Documents Per Domain: {3}                                  \n"\
        "============================================================\n"\
        "                                                            \n"\
        "OPTIONS:                                                    \n"\
        "  1 = Parse Input URL and Extract Keywords\n"\
        "  2 = Recommend Related Articles\n"\
        "  3 = Cross Lingual Analysis\n"\
        "  4 = Compare Related Keywords by Country\n"\
        "  5 = Quit                                                    \n"\
        "                                                              \n"\
        "============================================================\n".\
        format("Chicago Tribune", "WashingotnPost TImes", "Han Post", self.total_chicago)
        
        while True:
            sys.stderr.write(menu)
            option = input("Enter Option: ")
            if option == "1":
                self.parse_url()
            elif option == "2":
                self.get_related_articles()
            elif option == "3":
                self.cross_lingual_analysis()
            elif option == "4":
                self.compare_country()
            elif option == "5":
                exit(0)
            else:
                sys.stderr.write("Input seems not right, try again\n")


    def parse_url(self):
        menu = "Please type the url of newspaper within given 3 dominas: \n"
        sys.stderr.write(menu)
        url = input("URL: ")
        try:
            parser = NParser(url, stoplist_hash, positive_hash, negative_hash,\
                incrementer_hash, decrementer_hash, inverter)
            title, Keywords, sentiment = parser.search_url()
            print("============================================================\n")
            print('TITLE:')
            print("=====================")
            print(title[0:50] + '\n')
            print('Sentiment Analysis')
            print("=====================")
            print('{}\n'.format(sentiment))
            print('KEYWORDS:')
            print("=====================")
            print('\n'.join(Keywords.keys()))
            print("============================================================\n")
        except ValueError as e:
            print ('URL given ' + url + ' not valid. Please try again.')

        
    def get_related_articles(self):
        menu = "Please type keywords that you are interested separated by space(e.g. Trump taxes china ...etc: \n"
        sys.stderr.write(menu)
        url_query = input("Keywords: ")
        url_query = self.naive_stemming(url_query)
        stemmed_query = self.stemmer.stem(url_query).split()
        query_vector = defaultdict(int)

        synonym = []
        for t in url_query.split():
            syn = self.dictionary.synonym(t)
            if syn:
                synonym += syn
        stemmed_synonym = self.stemmer.stem(self.naive_stemming(' '.join(synonym))).split()

        for t in stemmed_query:
            if t not in self.stoplist_hash:
                query_vector[t] += 1

        for t in stemmed_synonym:
            if t not in self.stoplist_hash:
                query_vector[t] += 0.3

        corpus_vector = self.chicago_key_vector + self.washington_key_vector
        corpus_title = self.chicago_titles + self.washington_titles
        corpus_urls = self.chicago_urls + self.washington_urls
        corpus_sentiment = chicago_sentiment + washington_sentiment

        print("============================================================\n")
        print("                      RETREIVING DATA                      \n")
        print("============================================================\n")
        res_vector, doc_simula = self.get_retrieved_data(corpus_vector, query_vector)

        menu = "   ************************************************************\n"\
        "        Documents Most Similar 15 Articles to Given Topics       \n"\
        "  ************************************************************\n"\
        "  Similarity    Poliarity        Title                        \n"\
        "  ==========  ==============     ======================================\n"
        
        sys.stderr.write(menu)        

        for ind in range(15):
            index = res_vector[ind]
            similarity = doc_simula[index]

            title = corpus_title[index][:50]
            url = corpus_urls[index]
            sentiment = corpus_sentiment[index]

            sys.stderr.write("  {0:10.8f}  {1}   {2}\n".format(similarity, sentiment, title))
            sys.stderr.write("  URL: {}\n".format(url))

    def get_retrieved_data(self, corpus_vector, query_vector):
        total_number = len(corpus_vector) - 1

        doc_simula = []
        res_vector = []

        doc_simula.append(0)

        for index in range(1, total_number + 1):
            doc_simula.append(self.cosine_sim_a(query_vector, corpus_vector[index]))

        res_vector = sorted(range(1, total_number + 1), key = lambda x: -doc_simula[x])

        return res_vector, doc_simula

########################################################
## COSINE_SIM_A
##
## Computes the cosine similarity for two vectors
## represented as associate arrays. You can also pass the
## norm as parameter
##
## Note: You may do it in a much efficient way like
## precomputing norms ahead or using packages like
## "numpy", below provide naive implementation of that
########################################################

    def cosine_sim_a(self, vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
        if not vec1_norm:
            vec1_norm = sum(v * v for v in vec1.values())
        if not vec2_norm:
            vec2_norm = sum(v * v for v in vec2.values())

        # save some time of iterating over the shorter vec
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1

        # calculate the cross product
        cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
        return cross_product / (math.sqrt(vec1_norm * vec2_norm) + 1)

    def naive_stemming(self, text):
        text = text.split()
        temp = []
        for t in text:
            if "'" in t:
                t = t.split("'")
                temp.append(t[0])
            else:
                temp.append(t)
        return ' '.join(temp)

    def initialize_vec(self):
        self.chicago_key_vector.append(defaultdict(int))
        for word in open(CKEYS, 'r'):
            word = word.strip()
            if not word or word == ".I 0":
                continue  # Skip empty line

            if word[:2] == ".I":
                new_doc_vec = defaultdict(int)
                self.chicago_key_vector.append(new_doc_vec)
            elif word not in stoplist_hash and re.search('[a-zA-Z]', word):
                new_doc_vec[word] += 1
        
        self.washington_key_vector.append(defaultdict(int))
        for word in open(WKEYS, 'r'):
            word = word.strip()
            if not word or word == ".I 0":
                continue  # Skip empty line

            if word[:2] == ".I":
                new_doc_vec = defaultdict(int)
                self.washington_key_vector.append(new_doc_vec)
            elif word not in stoplist_hash and re.search('[a-zA-Z]', word):
                new_doc_vec[word] += 1

        self.han_key_vector.append(defaultdict(int))
        for word in open(HKEYS, 'r'):
            word = word.strip()
            if not word or word == ".I 0":
                continue  # Skip empty line

            if word[:2] == ".I":
                new_doc_vec = defaultdict(int)
                self.han_key_vector.append(new_doc_vec)
            elif word not in stoplist_hash and re.search('[a-zA-Z]', word):
                new_doc_vec[word] += 1

    def cross_lingual_analysis(self):
        menu = "Please type keywords that you are interested separated by space(e.g. Trump taxes china ...etc: \n"
        sys.stderr.write(menu)
        url_query = input("Keywords: ")
        url_query = self.naive_stemming(url_query)
        stemmed_query = self.stemmer.stem(url_query).split()    # list
        
        query_vector = defaultdict(int)
        for t in stemmed_query:
            if t not in self.stoplist_hash:
                query_vector[t] += 1

        corpus_vector = self.chicago_key_vector + self.washington_key_vector + self.han_key_vector
        corpus_title = self.chicago_titles + self.washington_titles + self.han_titles
        corpus_urls = self.chicago_urls + self.washington_urls + self.han_urls
        corpus_sentiment = self.chicago_sentiment + self.washington_sentiment + self.han_sentiment

        print("============================================================\n")
        print("                      RETREIVING DATA                      \n")
        print("============================================================\n")
        
        
        res_vector, doc_simula = self.get_retrieved_data(corpus_vector, query_vector)
        

        menu = "   ************************************************************\n"\
        "        Documents Most Similar 15 Articles to Given Topics       \n"\
        "  ************************************************************\n"\
        "  Similarity    Poliarity        Title                        \n"\
        "  ==========  ==============     ======================================\n"
        
        sys.stderr.write(menu)        

        for ind in range(15):
            index = res_vector[ind]
            similarity = doc_simula[index]

            title = corpus_title[index][:50]
            url = corpus_urls[index]
            sentiment = corpus_sentiment[index]

            sys.stderr.write("  {0:10.8f}  {1}   {2}\n".format(similarity, sentiment, title))
            sys.stderr.write("  URL: {}\n".format(url))

    def compare_country(self):
        
        menu = "Please type keywords that you want to compare by country: \n"
        sys.stderr.write(menu)
        
        url_query = input("Keywords: ")
        url_query = self.naive_stemming(url_query)
        stemmed_query = self.stemmer.stem(url_query).split()    # list
        query_vector = defaultdict(int)
        for t in stemmed_query:
            if t not in self.stoplist_hash:
                query_vector[t] += 1

        
        # corpus per country
        eng_corpus = self.chicago_key_vector + self.washington_key_vector
        kor_corpus = self.han_key_vector
        # sentiment per country
        eng_sentiment = self.chicago_sentiment + self.washington_sentiment
        kor_sentiment = self.han_sentiment

        print("============================================================\n")
        print("                      RETREIVING DATA                      \n")
        print("============================================================\n")
        
        eng_res_vector, eng_doc_simula = self.get_retrieved_data(eng_corpus, query_vector)
        eng_word_freq = defaultdict(int)
        eng_sent_score = 0
        for ind in range(60):
            index = eng_res_vector[ind]
            
            for word in eng_corpus[index]:
                eng_word_freq[word] += 1

            if eng_sentiment[index] == 'Positive':
                eng_sent_score += 2
            elif eng_sentiment[index] == 'Neutral~Positive':
                eng_sent_score += 1
            elif eng_sentiment[index] == 'Negative':
                eng_sent_score += -2
            elif eng_sentiment[index] == 'Negative~Neutral':
                eng_sent_score += -1

        kor_res_vector, kor_doc_simula = self.get_retrieved_data(kor_corpus, query_vector)
        kor_word_freq = defaultdict(int)
        kor_sent_score = 0
        for ind in range(60):
            index = kor_res_vector[ind]
            
            for word in kor_corpus[index]:
                kor_word_freq[word] += 1
            
            if kor_sentiment[index] == 'Positive':
                kor_sent_score += 3
            elif kor_sentiment[index] == 'Neutral~Positive':
                kor_sent_score += 1
            elif kor_sentiment[index] == 'Negative':
                kor_sent_score += -3
            elif kor_sentiment[index] == 'Negative~Neutral':
                kor_sent_score += -1

        sorted_eng_word = sorted([(value,key) for (key,value) in eng_word_freq.items()], reverse=True)
        sorted_kor_word = sorted([(value,key) for (key,value) in kor_word_freq.items()], reverse=True)
        
        sys.stderr.write("\nTop 15 associated words with your query in the American media are as follows:\n")
        for ind in range(15):
            if ind != 14:
                sys.stderr.write("{}, ".format(sorted_eng_word[ind][1]))
            else:
                sys.stderr.write("{}".format(sorted_eng_word[ind][1]))
        sys.stderr.write("\n")

        sys.stderr.write("Sentiment score for your query in the American media (higher is postitive): {}\n".format(eng_sent_score))
        
        sys.stderr.write("\nTop 15 Associatd words with your query in the Korean media are as follows:\n")
        for ind in range(15):
            if ind != 14:
                sys.stderr.write("{}, ".format(sorted_kor_word[ind][1]))
            else:
                sys.stderr.write("{}".format(sorted_kor_word[ind][1]))
        sys.stderr.write("\n")

        sys.stderr.write("Sentiment score for your query in the Korean media (higher is postitive): {}\n".format(kor_sent_score))

        if eng_sent_score > kor_sent_score:
            sys.stderr.write("\nAmerican media shows more positive sentiment towards your query topic\n")
        elif kor_sent_score > eng_sent_score:
            sys.stderr.write("\nKorean media shows more positive sentiment towards your query topic\n")
        else:
            sys.stderr.write("\nAmerican media and Korean media show equal sentiment towards your query topic\n")



if __name__ == '__main__':
    analysis = Newspaper()
    analysis.menu()



