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
			rare_vocab[item[0]] = i
	return common_vocab, rare_vocab

if os.path.exists("../data/de/wmt15.vocab"):
	vocab = json.load(open("../data/de/wmt15.vocab",'r'))
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

vocab = sorted(vocab.items(), key=lambda x: (-x[1], x[0]))
print("Total vocabulary size: "+str(len(vocab)))
common_vocab,rare_vocab = find_rare(vocab)

hman = open('dict.json', 'w')
hman.write(json.dumps({"common":common_vocab,'rare':rare_vocab}))
