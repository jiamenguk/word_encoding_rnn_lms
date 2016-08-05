#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json
import collections
from jutils import tokenizer

huffman = open('huffman.json.de', 'r')

'''
Load and build dictionary
'''

jsondict = json.load(huffman)
hd = jsondict['rare']
revd = {}

for key in hd.keys():
	tmp = "_".join(str(e) for e in hd[key])
	if tmp in revd:
		print "Oh dear, you have duplicate keys"
	revd[tmp] = key

huffman_dict={}

for key in hd.keys():
	sequence = hd[key]
	word = ""
	for i,j in enumerate(sequence):
		word += "s_"+str(j)+" "
	huffman_dict[key] = word.strip()

common_vocab = jsondict['common']

for word in common_vocab.keys():
	huffman_dict[word] = word

'''
Load stdin into an array of strings
'''

data = ""

outfile = open("wmt15.de.huff",'w')

inputfiles = ['../data/de/commoncrawl.de-en.de-sort.norm', '../data/de/news-commentary-v10.de-en.de-sort.norm', '../data/de/europarl-v7.de-sort.norm']
for filename in inputfiles:
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			words = [huffman_dict[word] for word in line]
			if len(words) == 0:
				continue
			data += " ".join(words)+"\n"
			if (i % 500) == 0:
				outfile.write(data.encode('utf8'))
				data = ""
			if (i % 100000) == 0:
				print i