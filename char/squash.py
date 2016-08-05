#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json
import collections
from jutils import tokenizer_norm as tokenizer

unksym = "<unk>"

huffman = open('dict.json', 'r')

'''
Load and build dictionary
'''

jsondict = json.load(huffman)

npdict = jsondict['common']

'''
Load stdin into an array of strings
'''

data = ""

outfile = open("wmt15.de.vanilla",'w')

inputfiles = ['../data/de/commoncrawl.de-en.de-sort.norm', '../data/de/news-commentary-v10.de-en.de-sort.norm', '../data/de/europarl-v7.de-sort.norm']
for filename in inputfiles:
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			words = [npdict[word] for word in line]
			if len(words) == 0:
				continue
			data += " ".join(words)+"\n"
			if (i % 500) == 0:
				outfile.write(data)
				data = ""
			if (i % 100000) == 0:
				print i