#!/usr/bin/python
import sys, json, re, unicodedata, os
import collections
import pywrapfst as fst
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-N', metavar='N', type=int,
                    help='size N')
parser.add_argument('-a', metavar='N', type=float, default=0.0, const=0.0, nargs="?",
                    help='Weight value')
parser.add_argument('-T', type=bool, default=False, const=True, nargs="?",
                    help='Use test')

args = parser.parse_args()
N = args.N
alpha = args.a
T = args.T
if T:
	NUMS = 2737
else:
	NUMS = 2169


scores = []
texts = []
for j in range(1,NUMS+1):
	text = []
	score = []
	if T:
		fname = '../1000best_news14/1000best_'+str(j)+'.txt'
	else:
		fname = '../1000best_news15/1000best_'+str(j)+'.txt'
	with open(fname, 'r') as infile:
		nlist = infile.readlines()
		n = min([len(nlist), N])
		score = [[[],[]] for i in range(n)]
		for i in range(n):
			line = nlist[i]
			line = line.replace('\n','').split('\t')
			score[i][0] = float(line[1])
			t = line[0].split()
			t = ' '.join(t[1:-1])
			text.append(t)

	if T:
		oname = '../scoring/vanilla_norm_1000best_news14/'+str(j)+'.txt'
	else:
		oname = '../scoring/vanilla_norm_1000best/best'+str(j)+'.txt'
	with open(oname,'r') as outfile:
		nlist = outfile.readlines()
		n = min([len(nlist), N])
		for i in range(n):
			line = nlist[i]
			line = line.split(' ||| ')
			score[i][1] = float(line[2])
	scores.append(score)
	texts.append(text)

print "Loaded scores and text"

while alpha <= 1.0:
	a1 = 1.0-alpha
	a2 = alpha
	s = []
	s_ev = []
	for n, nlist in enumerate(scores):
		s.append(min(enumerate(([i[0]*a1+i[1]*a2 for i in nlist])), key=lambda x: x[1])[0])

	with open('tmptest.txt', 'w') as tmpfile:
		for i in range(NUMS):
			tmpfile.write(texts[i][s[i]]+"\n")
	print alpha
	if T:
		os.system('python ../tutorial-ende-wmt15/scripts/apply_wmap.py -d i2s -m ../data/news14/wmap.testf.de < tmptest.txt > tmptest2.txt')
		os.system('../scoreBLEU.sh -t tmptest2.txt -r ../data/news14/testf.de')
	else:
		os.system('python ../tutorial-ende-wmt15/scripts/apply_wmap.py -d i2s -m ../tutorial-ende-wmt15/data/wmap.test15.de < tmptest.txt > tmptest2.txt')
		os.system('../scoreBLEU.sh -t tmptest2.txt -r ../test15.ref.de_std')
		break
	alpha += (0.01)