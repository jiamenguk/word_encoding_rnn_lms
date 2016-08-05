#!/usr/bin/python
import sys, json, re, unicodedata
import collections
from jutils import tokenizer_norm as tokenizer
# from jutils import tokenizer as tokenizer
import pywrapfst as fst

# huffword_2_id = json.load(open("../data/de/wmt15.de.huff-sort.wmap_norm", 'r'))

# huffman = open('huffman.json.de_norm', 'r')
# jsondict = json.load(huffman)
# hd = jsondict['rare']

# huffman_dict={}
# for key in hd.keys():
# 	sequence = hd[key]
# 	word = ["s_"+str(j) for j in sequence]
# 	huffman_dict[key] = word

# common_vocab = jsondict['common']

# for word in common_vocab.keys():
# 	huffman_dict[word] = [word]

# huffman_dict['<s>'] = ['<s>']
# huffman_dict['</s>'] = ['</s>']

# print "Built Huffman dictionary"
# '''
# Load and build dictionary
# '''
# tmp_set = set(huffman_dict.keys())
# tmp_set2 = set(huffword_2_id.keys())

# dictmap = dict()
# oid_2_huffw = dict()
# oid_2_huffid = dict()

# # with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
# with open('../data/wmap.testf.de','r') as infile:
# 	for i in infile:
# 		_tmp = i.replace('\n','').split()
# 		name = tokenizer(_tmp[0])
# 		# dictmap[_tmp[-1]] = name
# 		tmp = [huffman_dict[i] if i in tmp_set else ['<unk>'] for i in name]
# 		tmp = [i for l in tmp for i in l]
# 		oid_2_huffw[_tmp[-1]] = tmp
# 		oid_2_huffid[_tmp[-1]] = [huffword_2_id[i] for i in tmp if i in tmp_set2]

# de_map = open('huff_de.mapper_norm','w')
# de_map.write(json.dumps(oid_2_huffid))

# print "Built key to id"

oid_2_huffid = json.load(open("huff_de.mapper_norm", 'r'))

for j in range(1,2738):
	with open('../1000best_news14/1000best_'+str(j)+'.txt', 'r') as infile:
	# with open('../tmp2.txt', 'r') as infile:
		bestlist = infile.readlines()
		texts = []
		for line in bestlist:
			line = line.replace('\n','').split('\t')
			tmp = [oid_2_huffid[i] for i in line[0].split()]
			tmp = [str(i+1) for l in tmp for i in l]
			texts.append(tmp)
		with open('huff_1000best_news14/'+str(j)+'.txt','w') as outfile:
			for line in texts:
				line = ' '.join(line)
				line+='\n'
				outfile.write(line)