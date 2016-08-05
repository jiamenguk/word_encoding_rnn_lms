#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json, re, unicodedata
import collections
from jutils import tokenizer

'''
Load and build dictionary
'''
hd = json.load(open("dict.bpe.de",'r'))
common = json.load(open('dict.json','r'))['common']

tmp = hd
hd = {}
for key in tmp.keys():
	w = key.replace('</w>','')
	if w in common:
		hd[w] = ' '.join(tmp[key])

'''
Load stdin into an array of strings
'''

data = ""
outfile = open("wmt15.de.bpe_test",'w')

inputfiles = ['../data/de/commoncrawl.de-en.de-sort.norm', '../data/de/news-commentary-v10.de-en.de-sort.norm', '../data/de/europarl-v7.de-sort.norm']
for filename in inputfiles:
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			words = [hd[word] if word in hd else '<unk>' for word in line]
			if len(words) == 0:
				continue
			data += " ".join(words)+"\n"
			if (i % 50) == 0:
				outfile.write(data)
				data = ""
			if (i % 100000) == 0:
				print i