#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, io, json, os

import collections
from jutils import tokenizer

unksym = "<unk>"

vocab = collections
MAX_SIZE = 30000
SYM_SIZE = 300

class node(object):
	def __init__(self, nodes, value, name=None):
		self.nodes = nodes
		self.value = value
		self.name = name
	def __repr__(self):
		return str(self.value)

def node_sum(nodes):
	total_value = [node.value for node in nodes]
	return total_value

def build_vocab(line):
	counter = collections.Counter(line)
	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
	return count_pairs

def find_rare(vocab):
	i = 0
	common_vocab = dict()
	rare_vocab = collections.Counter('')
	for item in vocab:
		if i < MAX_SIZE:
			common_vocab[item[0]] = i
			i += 1
		else:
			rare_vocab[item[0]] = item[1]
			i += 1
	return common_vocab, rare_vocab

def getnode(n, prefix):
	global hd
	if n.nodes != None:
		for i, node in enumerate(n.nodes):
			p = prefix+[i]
			getnode(node, p)
	else:
		hd[n.name]=prefix

def huffman(rare_vocab):
	rare_vocab = sorted(rare_vocab.items(), key=lambda x: (x[1], x[0]))
	token = [0]
	j = 0
	huffman = dict()
	pd = []
	for item in rare_vocab:
		pd.append(node(None,item[1],item[0]))
	while True:
		if len(pd) < SYM_SIZE:
			break
		newnode = node(pd[0:SYM_SIZE-1],node_sum(pd[0:SYM_SIZE-1]), None)
		del pd[0:SYM_SIZE-1]
		pd.append(newnode)
		pd = sorted(pd, key=lambda x: x.value)

	for i, n in enumerate(pd):
		getnode(n,[i])

# if os.path.exists("../data/de/wmt15.vocab"):
# 	vocab = json.load(open("../data/de/wmt15.vocab",'r'))
# else:
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

vocab = sorted(vocab.items(), key=lambda x: (-x[1], x[0]))
print("Total vocabulary size: "+str(len(vocab)))
common_vocab,rare_vocab = find_rare(vocab)

hd = {}
huffman(rare_vocab)

jsondict = {"common":common_vocab, "rare": hd}

hman = open('huffman.json.de', 'w')
hman.write(json.dumps(jsondict))

l = [0, 0, 0, 0, 0, 0, 0]
for key in hd.keys():
	l[len(hd[key])] += 1

print l


