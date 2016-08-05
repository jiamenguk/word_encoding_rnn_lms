# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


"""Utilities for parsing PTB text files."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from random import shuffle

import collections
import os, re, json, time

import numpy as np
import tensorflow as tf
import math

def tokenizer(line):
	line = unicode(line, 'utf-8', errors='replace')
	line = line.lower()
	line = line.replace('\n',' </s>')
	# Remove Unknown words
	# line = line.replace('<unk> ','')
	line = '<s> '+line
	# line = re.sub(ur'\W',ur' ',line)
	# line.replace('.',' .')
	line = line.strip().split()
	return line

def _read_words(filename):
	with tf.gfile.GFile(filename, "r") as f:
		return f.read().replace("\n", "<eos>").split()

def _build_vocab_from_line(line):
	counter = collections.Counter(line)
	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
	return count_pairs

def _build_vocab_old(filename):
	data = _read_words(filename)

	counter = collections.Counter(data)
	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

	words, _ = list(zip(*count_pairs))
	word_to_id = dict(zip(words, range(len(words))))

	return word_to_id

def _build_vocab(filename):
	vocab = collections.Counter('')
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			vocab_line = _build_vocab_from_line(line)
			for item in vocab_line:
				vocab[item[0]] += item[1]
			if (i % 500000) == 0:
				print(i)
	count_pairs = sorted(vocab.items(), key=lambda x: (-x[1], x[0]))
	words, _ = list(zip(*count_pairs))
	word_to_id = dict(zip(words, range(len(words))))

	return word_to_id

def _file_to_word_ids_old(filename, word_to_id):
	data = _read_words(filename)
	return [word_to_id[word] for word in data]

def _file_to_word_ids(filename, word_to_id):
	data = []
	vocab = collections.Counter('')
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			line = tokenizer(line)
			data.append([word_to_id[word] for word in line])
			if (i % 500000) == 0:
				print(i)
	return data

def _load_from_ids(filename):
	data = []
	with open(filename,'r') as infile:
		for i, line in enumerate(infile):
			if i < 2000000:
				continue
			data.append(line.replace('\n','').split())
			if (i % 500000) == 0:
				print(i)
			if (i == 4000000):
				break
	return data

def _split_data(data):
	shuffle(data)
	N = len(data)
	n1 = N//20
	test_data = data[0:n1]
	# test_data = [item for sublist in test_data for item in sublist]
	valid_data = data[0:n1]
	# valid_data = [item for sublist in valid_data for item in sublist]
	train_data = data[n1:]
	a = sum([len(i) for i in train_data])/len(train_data)
	print(max([len(i) for i in train_data]))
	print(a)
	# train_data = [item for sublist in train_data for item in sublist]

	return train_data, valid_data, test_data


def split_data(data):
	data = data[0]+data[1]+data[2]
	shuffle(data)
	N = len(data)
	n1 = N//20
	n2 = N//50
	test_data = data[0:n1]
	# test_data = [item for sublist in test_data for item in sublist]
	valid_data = data[n1:n1+n2]
	# valid_data = [item for sublist in valid_data for item in sublist]
	train_data = data[n1+n2:]
	a = sum([len(i) for i in train_data])/len(train_data)
	print(max([len(i) for i in train_data]))
	print(a)
	# train_data = [item for sublist in train_data for item in sublist]

	return train_data, valid_data, test_data


def raw_data(data_path=None):

	train_path = data_path
	print('Building vocabulary')
	if os.path.exists(train_path+".wmap"):
		word_to_id  = json.load(open(train_path+".wmap", 'r'))
	else:
		word_to_id = _build_vocab(train_path)
		with open(train_path+".wmap",'w') as outfile:
			outfile.write(json.dumps(word_to_id))

	print('Converting words to IDs')
	if os.path.exists(train_path+".ids"):
		data = _load_from_ids(train_path+".ids")
	else:
		data = _file_to_word_ids(train_path, word_to_id)
		with open(train_path+".ids",'w') as outfile:
			for line in data:
				line = [str(i) for i in line]
				line = ' '.join(line)+'\n'
				outfile.write(line)

	train_data, valid_data, test_data = _split_data(data)
	vocabulary = len(word_to_id)
	return train_data, valid_data, test_data, vocabulary, word_to_id


def get_nbest_old(data_path, word_to_id):

	train_path = data_path
	data = _file_to_word_ids(train_path, word_to_id)
	test_data = data
	vocabulary = len(word_to_id)
	return test_data, vocabulary, word_to_id

def get_nbest(data_path, word_to_id):

	data = []
	with open(data_path,'r') as infile:
		lines = infile.readlines()
		for line in lines:
			line = line.replace('\n','')
			line = line.split()
			line = [int(i)-1 for i in line]
			data.append(line)
	test_data = data
	vocabulary = len(word_to_id)
	return test_data, vocabulary, word_to_id


def ptb_iterator(raw_data, batch_size, num_steps):
	"""Iterate on the raw PTB data.

	This generates batch_size pointers into the raw PTB data, and allows
	minibatch iteration along these pointers.

	Args:
		raw_data: one of the raw data outputs from ptb_raw_data.
		batch_size: int, the batch size.
		num_steps: int, the number of unrolls.

	Yields:
		Pairs of the batched data, each a matrix of shape [batch_size, num_steps].
		The second element of the tuple is the same data time-shifted to the
		right by one.

	Raises:
		ValueError: if batch_size or num_steps are too high.
	"""
	shuffle(raw_data)
	# raw_data = raw_data[:len(raw_data)//2]
	raw_data = [item for sublist in raw_data for item in sublist]
	raw_data = np.array(raw_data, dtype=np.int32)

	data_len = len(raw_data)
	batch_len = data_len // batch_size
	data = np.zeros([batch_size, batch_len], dtype=np.int32)
	for i in range(batch_size):
		data[i] = raw_data[batch_len * i:batch_len * (i + 1)]

	epoch_size = (batch_len - 1) // num_steps

	if epoch_size == 0:
		raise ValueError("epoch_size == 0, decrease batch_size or num_steps")

	for i in range(epoch_size):
		x = data[:, i*num_steps:(i+1)*num_steps]
		y = data[:, i*num_steps+1:(i+1)*num_steps+1]
		yield (x, y)

def rescore_iterator_old(raw_data, batch_size, num_steps, word_to_id):
	"""Iterate on the raw PTB data.

	This generates batch_size pointers into the raw PTB data, and allows
	minibatch iteration along these pointers.

	Args:
		raw_data: one of the raw data outputs from ptb_raw_data.
		batch_size: int, the batch size.
		num_steps: int, the number of unrolls.

	Yields:
		Pairs of the batched data, each a matrix of shape [batch_size, num_steps].
		The second element of the tuple is the same data time-shifted to the
		right by one.

	Raises:
		ValueError: if batch_size or num_steps are too high.
	"""
	# raw_data = [word_to_id['</s>']] + raw_data

	raw_data = np.array(raw_data, dtype=np.int32)

	data_len = len(raw_data)
	batch_len = data_len // batch_size
	data = np.zeros([batch_size, batch_len], dtype=np.int32)
	for i in range(batch_size):
		data[i] = raw_data[batch_len * i:batch_len * (i + 1)]
	epoch_size = (batch_len - 1) // num_steps

	if epoch_size == 0:
		raise ValueError("epoch_size == 0, decrease batch_size or num_steps")

	for i in range(epoch_size):
		x = data[:, i*num_steps:(i+1)*num_steps]
		y = data[:, i*num_steps+1:(i+1)*num_steps+1]
		yield (x, y)

def rescore_iterator(raw_data, batch_size, num_steps, word_to_id):
	"""Iterate on the raw PTB data.

	This generates batch_size pointers into the raw PTB data, and allows
	minibatch iteration along these pointers.

	Args:
		raw_data: one of the raw data outputs from ptb_raw_data.
		batch_size: int, the batch size.
		num_steps: int, the number of unrolls.

	Yields:
		Pairs of the batched data, each a matrix of shape [batch_size, num_steps].
		The second element of the tuple is the same data time-shifted to the
		right by one.

	Raises:
		ValueError: if batch_size or num_steps are too high.
	"""
	# raw_data = [word_to_id['</s>']] + raw_data

	epoch_size = raw_data.shape[1]

	if epoch_size == 0:
		raise ValueError("epoch_size == 0, decrease batch_size or num_steps")

	for i in range(0,epoch_size-1):
		x = raw_data[:, i*num_steps:(i+1)*num_steps]
		y = raw_data[:, i*num_steps+1:(i+1)*num_steps+1]
		yield (x, y)

def rescore_process(data, batch_size, word_to_id):
	test_data = []
	nums = int(math.ceil(len(data)/batch_size))
	while len(data) % batch_size != 0:
		data.append(data[0])
	for i in range(0,nums):
		raw_data = data[i:i+batch_size]
		maxlength = max([len(j) for j in raw_data])
		raw_data = np.array([[word_to_id['</s>']]+j+[word_to_id['<s>']]*(1+maxlength-len(j)) for j in raw_data], dtype=np.int32)
		yield raw_data