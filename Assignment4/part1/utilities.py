'''
This File contains utility functions which are used through out the Object
'''
import re
import os
from collections import Counter
from stopWords import *

wordCount = Counter()


def readFile(fileName):
	file = open(fileName, 'r')
	lines = file.readlines()
	file.close()
	return lines


def makeBOW(directory):
	makeBowModel(directory)
	bagOfWords = []
	for key, val in wordCount.iteritems():
		bagOfWords.append((key.lower().strip(), val))
	bagOfWords.sort(key=lambda tup: tup[1])
	return bagOfWords[-1000:]


def makeBowModel(directory):
	for i in range(0,2):
		folderpath = directory + '/spam' if i == 0 else directory + '/notspam'
		for path, dirs, files in os.walk(folderpath):
			for filename in files:
				if filename != 'cmds':
					x = os.path.join(path, filename)
					Lines = readFile(x)
					createBOW(Lines)


def cleanHtml(html):
		raw_html = ''.join(html)
		cleanr = re.compile('<.*?>')
		cleantext = re.sub(cleanr, '', raw_html)
		removeLines = re.compile('\n')
		cleantext = re.sub(removeLines, '', cleantext)
		removeSpecialCases = re.compile('[\\]x[0-9][0-9]')
		cleantext1 = re.sub(removeSpecialCases,'', cleantext)
		return cleantext1


def createBOW(lines):
	for line in lines:
		word = line.split(' ')
		for w in word:
			w = w.lower()
			w = ''.join(e for e in w if e.isalnum())
			if not 'nbsp' in w and w not in stopWords and w.isalpha():
				wordCount[w] += 1

class decisionTree:
	def __init__(self,col=-1,value=None,results=None,right=None,left=None, name=None):
		self.col = col
		self.value = value
		self.results = results
		self.right = right
		self.left = left
		self.name = name