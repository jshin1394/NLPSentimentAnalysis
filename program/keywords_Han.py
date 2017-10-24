import os
import sys
import re
from collections import OrderedDict, defaultdict

target = 'HanPost.stemmed.translated'
DIR = 'resource'
rf = open('./result/' + target, 'r')
wf = open('./result/' + target + '.key', 'w')
sf = open('./result/' + target + '.sentiment', 'w')

stoplist_hash = set()
for line in open('./resource/common_words', 'r'):
    if line:
        stoplist_hash.add(line.strip())

POSITIVE = DIR + "/positive.txt"
NEGATIVE = DIR + "/negative.txt"
INCREMENT = DIR + "/incrementer.txt"
DECREMENTER = DIR + "/decrementer.txt"
INVERTER = DIR + "/inverter.txt"
STOPLIST = DIR + "/common_words"

positive_hash = defaultdict(float)
negative_hash = defaultdict(float)
incrementer_hash = defaultdict(float)
decrementer_hash = defaultdict(float)
inverter = list()

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

def keywords(text):
    NUM_KEYWORDS = 30
    # of words before removing blacklist words
    if text:
        num_words = len(text)
        text = [x for x in text if x not in stoplist_hash and x != '']
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


def sentiment_analysis(text):
    vec1 = OrderedDict()
    for t in text:
        val = vec1.get(t, 0)
        vec1[t] = val + 1
    prev = ''
    sentiment_score = 0
    for t in vec1:
        if t in positive_hash:
            if prev in incrementer_hash:
                sentiment_score += positive_hash[t] * incrementer_hash[prev]
            elif prev in decrementer_hash:
                sentiment_score += positive_hash[t] * decrementer_hash[prev]
            elif prev in inverter:
                sentiment_score += positive_hash[t] * -1
            else:
                sentiment_score += positive_hash[t]
        elif t in negative_hash:
            if prev in incrementer_hash:
                sentiment_score += negative_hash[t] * incrementer_hash[prev]
            elif prev in decrementer_hash:
                sentiment_score += negative_hash[t] * decrementer_hash[prev]
            elif prev in inverter:
                sentiment_score += negative_hash[t] * -1
            else:
                sentiment_score += negative_hash[t]

    if sentiment_score < 25 and sentiment_score >= 0:
        return 'Neutral~Positive'
    elif sentiment_score > 25:
        return 'Positive'
    elif sentiment_score < 0 and sentiment_score > -25:
        return 'Negative~Neutral'
    else:
        return 'Negative'



for line in rf:
    word = line.strip()
    
    if not word or word == ".I 0":
        continue  # Skip empty line
    
    if word[:2] == ".I":
        wf.write(word + '\n')
    elif word[0] == '/':
        word_list = re.split('[/ ]', word.strip())

        kws = keywords(word_list).keys()
        for k in kws:
            wf.write('{}\n'.format(k))
        sentiment = sentiment_analysis(word_list)
        sf.write('{}\n'.format(sentiment))




