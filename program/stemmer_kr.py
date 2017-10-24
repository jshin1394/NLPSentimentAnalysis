# from konlpy.tag import Kkma
from konlpy.tag import Komoran
# from konlpy.utils import pprint

import re
import string
import sys


def write_stemmed():

	raw_file = open(filename + '.raw', 'w')
	title_file = open(filename + '.titles', 'w')
	url_file = open(filename + '.url', 'w')
	stem_file = open(filename + '.stemmed', 'w')

	num = 0
	url = ''
	title = ''
	text = ''
	prev = ''
	for line in body:
		# if not empty line
		line = line.strip()
		if line != '':
			# new line, clear everything
			if line[:2] == '.I':
				head = ''
				title = ''
				url = ''
				text = ''
			elif prev == '.U':
				url = line
			elif prev == '.T':
				title = line
			# .B section is valid
			elif prev == '.B':
				num += 1
				head = '.I ' + str(num)
				raw_file.write(head + '\n')
				raw_file.write(line + '\n')
				title_file.write(title + '\n')
				url_file.write(url + '\n')
				stem_file.write(head + '\n')
				raw = ''.join([ch for ch in line if ch not in string.punctuation and ch not in avoid_list])
				my_list = komoran.pos(raw)
				for item in my_list:
					if item[1] in include_list:
						stem_file.write(item[0] + '\n')
				stem_file.write('\n')

			prev = line
		
	raw_file.close()
	title_file.close()
	url_file.close()
	stem_file.close()


def print_freq():
	num_words = 0
	word_pair = {}

	for line in body:
		line = line.strip()
		if line:
			if not re.match('^.I [0-9]+$', line) and not re.match('^http+', line):
				raw = line.strip()
				raw = ''.join([ch for ch in raw if ch not in string.punctuation and ch not in avoid_list])
				my_list = komoran.pos(raw)
				for item in my_list:
					if item[1] in include_list:
						num_words += 1
						word_pair[item[0]] = word_pair.get(item[0], 0) + 1

	[print("%s,%d" % (item[1].strip(), item[0])) for item in sorted([(value,key) for (key,value) in word_pair.items()], reverse = True)]


if __name__ == '__main__':
	
	filename = sys.argv[1]
	stem_freq = sys.argv[2]

	avoid_list = ['“','”','‘','’','“','”','.',',']
	include_list = ['NNP','NNG','VV','VA']

	komoran = Komoran()
	infile = open(filename, 'r')
	body = infile.readlines()
	
	if stem_freq == "stem":
		write_stemmed()
	elif stem_freq == "freq":
		print_freq()
	
	infile.close()

