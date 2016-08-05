# Copyright 2015 Jiameng Gao. All Rights Reserved.
#
# Licensed under the MIT License
# ==============================================================================
import re, unicodedata

def tokenizer_norm(line):
	line = unicode(line, 'utf-8', errors='replace')
	line = line.lower()
	line.replace('\n','')
	line = unicodedata.normalize('NFKD',line)
	line = line.encode('ascii','ignore')
	# line = re.sub(ur'\W',ur' ',line)
	line = re.sub(ur'-',ur' ',line)
	line = re.sub(ur'[0-9]',ur'0',line)
	line = re.sub(ur' +', ur' ', line)
	line = re.sub(ur'0+', ur'0', line)
	# line = re.sub(ur'(0 )+', ur'0 ', line)
	line = line.strip().split()
	return line

def tokenizer(line):
	line = unicode(line, 'utf-8', errors='replace')
	line.replace('\n','')
	# line = re.sub(ur'\W',ur' ',line)
	line = re.sub(ur'[0-9]',ur'0',line)
	line = re.sub(ur' +', ur' ', line)
	line = re.sub(ur'0+', ur'0', line)
	# line = re.sub(ur'(0 )+', ur'0 ', line)
	line = line.strip().split()
	return line