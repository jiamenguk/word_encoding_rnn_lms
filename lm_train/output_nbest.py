#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json, re, unicodedata
import collections,fileinput

uncompfile = fileinput.input()

dictmap = dict()
with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
	test_dict_file = infile.readlines()
	test_dict = dict()
	for i in test_dict_file:
		_tmp = i.replace('\n','').split()
		name = _tmp[0]
		dictmap[_tmp[-1]] = name

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
		nbest[i].append(words)

for i, line in enumerate(uncompfile):
	line = line.split(' || ')
	num = int(line[0])
	print nbest[i][num]
