from nltk.stem import *
import re
import string
import sys
import csv

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
			
			# in the .B section
			elif prev == '.B':
				num += 1

				head = '.I ' + str(num)
				raw_file.write(head + '\n')
				raw_file.write(line + '\n')
				title_file.write(title + '\n')
				url_file.write(url + '\n')
				
				stem_file.write(head + '\n')
				raw = line.replace('’s','').split()
				for item in raw:
					item = ''.join([ch for ch in item if ch not in string.punctuation and ch not in avoid_list])
					stem_file.write(stemmer.stem(item) + '\n')
				stem_file.write('\n')
			
			prev = line
		

	raw_file.close()
	title_file.close()
	url_file.close()
	stem_file.close()
	


def stem_dictionary():
	infile = open(filename,'r')
	outfile = open(filename + '.stemmed', 'w')
	
	# infile: headword_lang,head,pos,value
	csvreader = csv.DictReader(infile)
	outfile.write('head,headword_lang,pos,value\n')
	for line in csvreader:
		word_stem = stemmer.stem(line['value'])
		outfile.write('%s,%s,%s,"%s"\n' % (line['headword_lang'], line['head'], line['pos'], word_stem))
	
	infile.close()	
	outfile.close()


def stem_dictionary2():
	infile = open(filename,'r')
	outfile = open(filename + '.stemmed', 'w')
	
	# infile: kor, eng
	outfile.write('kor,eng\n')
	body = infile.readlines()

	for line in body:
		element = line.strip().split('\t')
		word_stem = stemmer.stem(element[1])
		# print(element[0], word_stem)
		outfile.write('%s,"%s"\n' % (element[0], word_stem))

	infile.close()	
	outfile.close()



def print_freq():
	
	num_words = 0
	word_pair = {}

	for line in body:
		line = line.strip()
		if line:
			if not re.match('^.I [0-9]+$', line) and not re.match('^http+', line):
				raw = line.strip().replace('’s','').split()
				for item in raw:
					item = ''.join([ch for ch in item if ch not in string.punctuation and ch not in avoid_list])
					num_words += 1
					word_pair[item] = word_pair.get(item, 0) + 1

	[print("%s,%d" % (item[1].strip(), item[0])) for item in sorted([(value,key) for (key,value) in word_pair.items()], reverse = True)]


	



if __name__ == '__main__':
	
	filename = sys.argv[1]
	stem_freq = sys.argv[2]

	avoid_list = ['“','”','‘','’','“','”','.',',']

	stemmer = SnowballStemmer("english")
	# stemmer = PorterStemmer()
	infile = open(filename, 'r')
	body = infile.readlines()
	
	avoid_list = ['’s', '',]
	if stem_freq == "stem":
		write_stemmed()
	elif stem_freq == "freq":
		print_freq()
	elif stem_freq == "dic":
		stem_dictionary()
	elif stem_freq == "dic2":
		stem_dictionary2()

		
	infile.close()
