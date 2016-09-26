import sys, json, re, unicodedata, os
from jutils import tokenizer

import collections

unksym = "<unk>"

vocab = collections
MAX_SIZE = 50000
SYM_SIZE = 100

def build_vocab(line):
	counter = collections.Counter(line)
	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
	return count_pairs

def append_vocab(vocab):
	new = []
	for item in vocab:
		new.append((list(item[0]+"."),item[1]))
	return new

def break_down(item):
	p1 = zip(item[:-1],item[1:])
	pairs = ['_'.join(i) for i in p1]
	return pairs

def make_list(changed):
	i = 0
	pairs = collections.Counter('')
	for item in changed:
		word = break_down(item[0])
		for a in word:
			pairs[a] += item[1]
	return pairs

def vocab_update(vocab, new_pair, joined):
	new_vocab = vocab
	changed = []
	for i,item in enumerate(vocab):
		word = '_'.join(item[0])
		pattern = re.compile(r'(?<!\S)' + re.escape(word) + r'(?!\S)')
		if new_pair in word:
			i1 = word.replace(new_pair,joined).split('_')
			_tmp = (i1,item[1])
			changed.append(_tmp)
			new_vocab[i] = _tmp
	return new_vocab, changed

def prune(pairs):
	for item,freq in list(pairs.items()):
		if freq < 3:
			del pairs[item]

if os.path.exists(sys.argv[1]+".vocab"):
	vocab = json.load(open(sys.argv[1]+".vocab",'r'))
else:
	vocab = collections.Counter('')
	with open(sys.argv[1],'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			vocab_line = build_vocab(line)
			for item in vocab_line:
				vocab[item[0]] += item[1]
			if (i % 100000) == 0:
				print i
	with open(sys.argv[1]+".vocab",'w') as outfile:
		outfile.write(json.dumps(vocab))

print len(vocab.keys())

vocab = sorted(vocab.items(), key=lambda x: (-x[1], x[0]))
vocab = append_vocab(vocab)
new_pairs = set('abcdefghijklmnopqrstuvwxyz.')
pairs = dict()
changed = vocab
# bpe_dict = list(units)
gather = dict()
for i in range(0, 3000):
	new_dict = make_list(changed)
	pairs.update(new_dict)
	# count_pairs = sorted(pairs.items(), key=lambda x: -x[1])
	new_pair = max(pairs, key=pairs.get)
	if pairs[new_pair] < 2 or len(pairs.keys())==0:
		break
	threshold = pairs[new_pair] * i/(i+10000.0)
	gather[new_pair] = pairs[new_pair]
	pairs[new_pair] = 0
	# bpe_dict.append(new_pair)
	tmp = new_pair.replace('_','')
	vocab, changed = vocab_update(vocab, new_pair, tmp)
	if (i % 100) == 0:
		prune(pairs)
		print i
		# print pairs

bpe_dict = {}
for item in vocab:
	word = ''.join(item[0])
	bpe_dict[word] = item[0]

with open("dict.bpe",'w') as outfile:
	outfile.write(json.dumps(gather))
