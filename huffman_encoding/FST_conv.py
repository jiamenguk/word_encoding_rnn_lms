#!/usr/bin/python
import sys, json, re, unicodedata
import collections
from jutils import tokenizer_norm as tokenizer
# from jutils import tokenizer as tokenizer
import pywrapfst as fst

huffword_2_id = json.load(open("../data/de/wmt15.de.huff-sort.wmap_norm", 'r'))

huffman = open('huffman.json.de_norm', 'r')
jsondict = json.load(huffman)
hd = jsondict['rare']

huffman_dict={}
for key in hd.keys():
	sequence = hd[key]
	word = ["s_"+str(j) for j in sequence]
	huffman_dict[key] = word

common_vocab = jsondict['common']

for word in common_vocab.keys():
	huffman_dict[word] = [word]

huffman_dict['<s>'] = ['<s>']
huffman_dict['</s>'] = ['</s>']

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
	test_dict_file = infile.readlines()
	test_dict = dict()
	for i in test_dict_file:
		_tmp = i.replace('\n','').split()
		name = tokenizer(_tmp[0])
		# dictmap[_tmp[-1]] = name
		tmp = [huffman_dict[i] if i in tmp_set else ['<unk>'] for i in name]
		tmp = [i for l in tmp for i in l]
		# oid_2_huffw[_tmp[-1]] = tmp
		oid_2_huffid[_tmp[-1]] = [huffword_2_id[i]+1 for i in tmp if i in tmp_set2]

oid_2_huffid['1'] = [1]
oid_2_huffid['2'] = [2]
oid_2_huffid['3'] = [3]

# de_map = open('huff_de.mapper','w')
# de_map.write(json.dumps(oid_2_huffid))

print "Built key to id"

# oid_2_huffid = json.load(open("huff_de.mapper", 'r'))

f = fst.Fst()
start = f.add_state()
final = f.add_state()
f.set_start(start)
f.set_final(final, '0')
for j, key in enumerate(oid_2_huffid.keys()):
	ids = oid_2_huffid[key]
	if len(ids) == 0:
		tmp = fst.Arc(int(key),0,'0',final)
		f.add_arc(start, tmp) 
	elif len(ids) == 1:
		tmp = fst.Arc(int(key),ids[0],'0',final)
		f.add_arc(start, tmp)
	else:
		tmp_state = f.add_state()
		tmp = fst.Arc(int(key),ids[0],'0',tmp_state)
		f.add_arc(start, tmp)
		s_state = tmp_state
		for i in range(1,len(ids)):
			tmp_state = f.add_state()
			tmp = fst.Arc(0, ids[i],'0',tmp_state)
			f.add_arc(s_state, tmp)
			s_state = tmp_state
		f.set_final(tmp_state)

print "Built FST"

oid_2_huffid = f
# oid_2_huffid = fst.determinize(oid_2_huffid)
oid_2_huffid.closure()
oid_2_huffid.arcsort(sort_type='ilabel')

oid_2_huffid.write('vocab_map_closed.fst')

# print "Closed FST"

# oid_2_huffid = fst.Fst.read('vocab_map_closed.fst')

# for i in xrange(1,2170):
# 	if (i % 100) == 0:
# 		print i
# 	A = fst.Fst.read("../tutorial-ende-wmt15/hiero/lats/"+str(i)+".fst")
# 	A.arcsort(sort_type='olabel')
# 	B = fst.compose(A,oid_2_huffid)
# 	B.project(project_output=True)
# 	B.rmepsilon()
# 	C = fst.determinize(B)
# 	C.minimize()
# 	if B.num_states == 0:
# 		print i
# 	B.write("huff_lats/"+str(i)+".fst")