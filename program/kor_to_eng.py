import string
import sys
import csv
import re

def translate_freq():
	infile_dic = open('Korean2.tsv.stemmed', 'r')
	infile = open('HanPost.freq', 'r')
	outfile = open('HanPost.freq.translated', 'w')

	kor_to_eng = {}
	csvreader = csv.DictReader(infile_dic)
	for line in csvreader: # infile_dic: korword_lang,kor,pos,eng
		kor_to_eng[line['kor'].strip()] = kor_to_eng.get(line['kor'], '') + '/' + line['eng'].strip()
	

	body = infile.readlines()
	for line in body:
		translation = ''
		column = line.strip().split(',')
		for target in kor_to_eng.keys():
			if re.match(column[0],target):
				translation = translation + kor_to_eng[target].strip().replace('\n','')
		if translation != '':
			outfile.write('"%s",%s\n' % (translation, column[1]))

	infile_dic.close()
	infile.close()
	outfile.close()



def translate_stem():
	infile_dic = open('Korean2.tsv.stemmed', 'r')
	infile = open('HanPost.stemmed', 'r')
	outfile = open('HanPost.stemmed.translated', 'w')
	

	kor_to_eng = {}
	csvreader = csv.DictReader(infile_dic)
	for line in csvreader: # infile_dic: korword_lang,kor,pos,eng
		kor_to_eng[line['kor'].strip()] = kor_to_eng.get(line['kor'], '') + '/' + line['eng'].strip()
	

	body = infile.readlines()
	translation = ''
	for line in body:
		line = line.strip()
		if line != '':
			if line[:2] == '.I':
				outfile.write(line + '\n')
				# print(line)
				translation = ''
			else:
				translation = ''
				for target in kor_to_eng.keys():
					if re.match(line,target):
						translation = translation + kor_to_eng[target].strip()
				
				if translation != '':
					outfile.write(translation + '\n')
				# print(translation)
				
	
	infile_dic.close()
	infile.close()
	outfile.close()



if __name__ == "__main__":
	option = sys.argv[1]
	if option == 'stem':
		translate_stem()
	elif option == 'freq':
		translate_freq()
		