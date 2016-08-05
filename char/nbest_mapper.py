#!/usr/bin/python
import sys, json, re, unicodedata
import collections
from jutils import tokenizer_norm as tokenizer
# from jutils import tokenizer as tokenizer
import pywrapfst as fst

huffword_2_id = json.load(open("../data/de/wmt15.de.char.wmap", 'r'))
huffword_2_id['<unk>'] = []

huffman = open('dict.json', 'r')
jsondict = json.load(huffman)

huffman_dict = jsondict['common']

huffman_dict['<s>'] = '<s>'
huffman_dict['</s>'] = '</s>'

print "Built Huffman dictionary"
'''
Load and build dictionary
'''
tmp_set = set(huffman_dict.keys())
tmp_set2 = set(huffword_2_id.keys())

dictmap = dict()
oid_2_huffw = dict()
oid_2_huffid = dict()

with open('../tutorial-ende-wmt15/data/wmap.test15.de','r') as infile:
# with open('../data/news14/wmap.testf.de','r') as infile:
	for i in infile:
		_tmp = i.replace('\n','').split()
		name = tokenizer(_tmp[0])
		if len(name) == 0:
			oid_2_huffid[_tmp[-1]] = []
			continue
		if name[0] == '<epsilon>':
			oid_2_huffid[_tmp[-1]] = []
			continue
		# tmp = [word+ for word in name]
		tmp = [huffman_dict[word].split() if word in tmp_set else list(word)+['</w>'] for word in name]
		# oid_2_huffw[_tmp[-1]] = tmp
		oid_2_huffid[_tmp[-1]] = [huffword_2_id[i] for word in tmp for i in word if i in tmp_set2]

de_map = open('de.mapper_norm','w')
de_map.write(json.dumps(oid_2_huffid))

print "Built key to id"

# oid_2_huffid = json.load(open("de.mapper_norm", 'r'))

# rev_dict = dict((value, key) for (key, value) in huffword_2_id.iteritems())

# for j in range(1,2738):
# 	with open('../1000best_news14/1000best_'+str(j)+'.txt', 'r') as infile:
# 	# with open('../1000best_news15/1000best_'+str(j)+'.txt', 'r') as infile:
# 	# with open('../tmp2.txt', 'r') as infile:
# 		bestlist = infile.readlines()
# 		texts = []
# 		for line in bestlist:
# 			line = line.replace('\n','').split('\t')
# 			tmp = [oid_2_huffid[i] for i in line[0].split()]
# 			# print [rev_dict[i] for l in tmp for i in l]
# 			# print tmp
# 			tmp = [str(i[0]+1) for l in tmp for i in l if i != []]
# 			texts.append(tmp)
# 		with open('char_1000best_news14/'+str(j)+'.txt','w') as outfile:
# 		# with open('char_1000best_news15/'+str(j)+'.txt','w') as outfile:
# 			for line in texts:
# 				line = ' '.join(line)
# 				line+='\n'
# 				outfile.write(line)