#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json, re, unicodedata
import collections
from jutils import tokenizer

huffman = open('huffman.json', 'r')

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

print "Built Huffman dictionary"

dictmap = dict()
with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
	test_dict_file = infile.readlines()
	test_dict = dict()
	for i in test_dict_file:
		_tmp = i.replace('\n','').split()
		name = tokenizer(_tmp[0])
		dictmap[_tmp[-1]] = ' '.join(name)

print "Built key to vocab"

nbest = []
i_old = -1
with open('../tutorial-ende-wmt15/hiero/100best.txt') as nbestfile:
	for line in nbestfile:
		line = line.replace('\n','')
		line = line.split(' ||| ')
		i = int(line[0])
		if i != i_old:
			nbest.append([])
			i_old = i
		words = ' '.join([dictmap[w] for w in line[1].split()])
		words = words.encode('utf-8','ignore')
		words = tokenizer(words)
		nbest[i].append(words)

print "Got nbest list"

bag = set()
for n in nbest:
	for line in n:
		bag.update(set(line))

tmp = set(huffman_dict.keys())

unks = []

map2huff = dict()
for name in bag:
	if name not in tmp:
		unks.append(name)
	else:
		map2huff[name] = huffman_dict[name]

print len(bag)
print len(unks)
print unks
for name in unks:
	map2huff[name] = "<unk>"

for i,n in enumerate(nbest):
	with open('../data/nbest_huff/'+str(i)+'.words','w') as outfile:
		for line in n:
			words = ' '.join([map2huff[w] for w in line])
			outfile.write(words+"\n")