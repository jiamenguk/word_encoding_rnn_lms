#!/usr/bin/env python
import time, sys, io, json, datetime, re, unicodedata, csv
import numpy as np
import fileinput


class node(object):
	def __init__(self, one, zero, value):
		self.one = one
		self.zero = zero
		self.value = value
	def __repr__(self):
		return str(self.value)

def getnode(n, prefix):
	global hd
	if n.zero != None:
		p0 = prefix+[0]
		p1 = prefix+[1]
		getnode(n.zero, p0)
		getnode(n.one, p1)
	else:
		hd[n.one]=prefix
		return n.one, prefix

compfile = fileinput.input()
huffman = open('huffman.json', 'r')

hd = json.load(huffman)
revd = {}

for key in hd.keys():
	hd[key] = "".join(str(e) for e in hd[key])
	if hd[key] in revd:
		print "Oh dear, you have duplicate keys"
	revd[hd[key]] = key

l = ''

for i, line in enumerate(compfile):
	l += line.replace('\n','')

decode = list(l)
decoded = []

bits = ""

for a in decode:
	bits += a
	if bits in revd:
		decoded += [revd[bits]]
		bits = ""

b = ""

for word in decoded:
	a = word
	a = int(a)
	while a > 0:
		b += '0'
		a = a-1
	b += '1'

if len(b) < 10000:
	diff = 10000-len(b)
	while diff > 0:
		b += '0'
		diff = 10000-len(b)

print b