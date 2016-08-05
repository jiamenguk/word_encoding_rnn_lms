#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, io, json, os

import collections
from jutils import tokenizer_norm as tokenizer

unksym = "<unk>"

vocab = collections
MAX_SIZE = 30000
SYM_SIZE = 300

if os.path.exists("../data/de/wmt15.vocab_norm"):
	vocab = json.load(open("../data/de/wmt15.vocab_norm",'r'))
else:
	inputfiles = ['../data/de/commoncrawl.de-en.de-sort.norm', '../data/de/news-commentary-v10.de-en.de-sort.norm', '../data/de/europarl-v7.de-sort.norm']
	vocab = collections.Counter('')
	for filename in inputfiles:
		with open(filename,'r') as infile:
			for i, line in enumerate(infile):
				line = tokenizer(line)
				vocab_line = build_vocab(line)
				for item in vocab_line:
					vocab[item[0]] += item[1]
				if (i % 100000) == 0:
					print i
	with open("../data/de/wmt15.vocab",'w') as outfile:
		outfile.write(json.dumps(vocab))

vocab_dict = {key: list(key)+['</w>'] for key in vocab}
vdict = {key: ' '.join(value) for key, value in vocab_dict.iteritems()}

print("Total vocabulary size: "+str(len(vocab)))

hman = open('dict.json', 'w')
hman.write(json.dumps({"common":vdict}))
