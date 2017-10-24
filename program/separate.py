file = 'HanPost'

rf = open('result/' + file, 'r')
wf = open('result/' + file + '.raw', 'w')
tf = open('result/' + file + '.titles', 'w')
uf = open('result/' + file + '.url', 'w')


num = ''
url = ''
text = ''
prev = ''
for line in rf:
	word = line.strip()
	if word[:2] == '.I':
		url = ''
		text = ''
		head = word

	elif prev == '.U':
		uf.write(word + '\n')
	elif prev == '.T':
		tf.write(word + '\n')
	elif prev == '.B':
		wf.write(head + '\n')
		wf.write(word + '\n')

	prev = word