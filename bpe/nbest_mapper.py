#!/usr/bin/python
import sys, json, re, unicodedata, os
import collections
from jutils import tokenizer_norm as tokenizer
# from jutils import tokenizer as tokenizer
import pywrapfst as fst

def addwords(rules, unks, encodeword_2_id):
	bpe = dict()
	unks = list(unks)
	words = [word.replace('`','') for word in unks]
	words = [list(unk)[:-4]+['</w>'] for unk in words]
	words = [' '.join(unk) for unk in words]
	for rule in rules:
		pair1 = ' '.join(rule)
		reppair = ''.join(rule)
		words = [word.replace(pair1,reppair) for word in words]
	words = [word.split() for word in words]
	bpe = dict((unk, p) for (unk, p) in zip(unks, words))
	return bpe

encodeword_2_id = json.load(open("../data/de/wmt15.de.bpe.wmap_norm", 'r'))

encoded = open('dict.bpe.de', 'r')
encoded_dict = json.load(encoded)

encoded_dict['<s>'] = ['<s>']
encoded_dict['</s>'] = ['</s>']

print "Built BPE dictionary"
'''
Load and build dictionary
'''
pairs = open('pairs.txt','r').readlines()
rules = []
for line in pairs:
	line = line.replace('\n','')
	rules.append(line.split())

dictmap = dict()
oid_2_huffw = dict()
oid_2_encodeid = dict()

unks = set()

tmp_set = set(encoded_dict.keys())
tmp_set2 = set(encodeword_2_id.keys())

with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
# with open('../data/news14/wmap.testf.de','r') as infile:
	for i in infile:
		_tmp = i.replace('\n','').split()
		name = tokenizer(_tmp[0])
		name = [j+"</w>" for j in name]
		empty = [j for j in name if j not in tmp_set]
		if empty != []:
			unks = unks.union(empty)

print "Found unknown words"

d = addwords(rules, unks, encodeword_2_id)
encoded_dict.update(d)

print "Added unknown words"

unks = set()

tmp_set = set(encoded_dict.keys())
tmp_set2 = set(encodeword_2_id.keys())

with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
# with open('../data/news14/wmap.testf.de','r') as infile:
	for i in infile:
		_tmp = i.replace('\n','').split()
		name = tokenizer(_tmp[0])
		name = [j+"</w>" for j in name]
		empty = [j for j in name if j not in tmp_set]
		if empty != []:
			unks = unks.union(empty)
		tmp = [encoded_dict[j] if j in tmp_set else ['<unk>'] for j in name]
		tmp = [j for l in tmp for j in l]
		# oid_2_huffw[_tmp[-1]] = tmp
		# oid_2_encodeid[_tmp[-1]] = [encodeword_2_id[i] if i in tmp_set2 else ['<unk>'] for i in tmp]
		oid_2_encodeid[_tmp[-1]] = [encodeword_2_id[i] for i in tmp if i in tmp_set2]

oid_2_encodeid['1'] = [encodeword_2_id['<s>']]
oid_2_encodeid['2'] = [encodeword_2_id['</s>']]

de_map = open('de_2015.mapper_norm','w')
de_map.write(json.dumps(oid_2_encodeid))

print "Built key to id"

# oid_2_encodeid = json.load(open("bpe_de.mapper_norm", 'r'))

# path = 'bpe_1000best_news14/'
# if not os.path.exists(path):
# 	os.makedirs(path)

# for j in range(1,2738):
# 	with open('../1000best_news14/1000best_'+str(j)+'.txt', 'r') as infile:
# 		bestlist = infile.readlines()
# 		texts = []
# 		for line in bestlist:
# 			line = line.replace('\n','').split('\t')
# 			# print [oid_2_huffw[i] for i in line[0].split()]
# 			tmp = [oid_2_encodeid[i] for i in line[0].split()]
# 			# print tmp
# 			tmp = [str(i+1) for l in tmp for i in l]
# 			texts.append(tmp)
# 		with open(path+str(j)+'.txt','w') as outfile:
# 			for line in texts:
# 				line = ' '.join(line)
# 				line+='\n'
# 				outfile.write(line)