from utilities import *
import os
import math
from stopWords import *
from collections import Counter

import pickle

documentMatrix = []
documentBinaryMatrix = []
classified = []
classifiedBinary = []

def readTreeModelFile(modelFile):
	with open(modelFile, 'rb') as file:
		return pickle.load(file)

def classify(rows,tree):
	if tree.results!=None:
		return tree.results
	else:
		values=rows[tree.col]
		branch=None
		if values>=tree.value:
			branch=tree.right
		else:
			branch=tree.left
		return classify(rows,branch)

def createMatrix(lines, mode, bow):
	array = []
	wd = []
	spamWordCount = Counter()

	for line in lines:
		line = cleanHtml(line)
		word = line.split(' ')
		for w in word:
			w = w.lower()
			words = ''.join(e for e in w if e.isalnum())
			if not 'nbsp' in words and words not in stopWords and words.isalpha():
				spamWordCount[words] += 1
				if words not in wd:
					wd.append(words)

	for word in bow:
		if word[0] in wd:
			array.append(spamWordCount[word[0]])
		else:
			array.append(0)

	if mode == 'spam':
		array.append('spam')
	else:
		array.append('nonspam')

	documentMatrix.append(array)



def createBinaryMatrix(lines, mode, bow):
	array = []
	wd = []
	spamWordCount = Counter()

	for line in lines:
		line = cleanHtml(line)
		word = line.split(' ')
		for w in word:
			w = w.lower()
			words = ''.join(e for e in w if e.isalnum())
			if not 'nbsp' in words and words not in stopWords and words.isalpha():
				if words not in wd:
					wd.append(words)

	for word in bow:
		if word[0] in wd:
			array.append(1)
		else:
			array.append(0)

	if mode == 'spam':
		array.append('spam')
	else:
		array.append('nonspam')

	documentBinaryMatrix.append(array)



def addTestData(bow, path1):
	counter = 0

	for i in range(0,2):
		folderpath = path1 + '/spam' if i == 0 else path1 + '/notspam'
		for path, dirs, files in os.walk(folderpath):
			for filename in files:
				counter += 1
				if filename != 'cmds':
					x = os.path.join(path, filename)
					Lines = readFile(x)
					createMatrix(Lines, 'spam', bow) if i == 0 else createMatrix(Lines, 'notspam', bow)
					createBinaryMatrix(Lines, 'spam', bow) if i == 0 else createBinaryMatrix(Lines, 'notspam', bow)

def classifyData(tree):
	for data in documentMatrix:
		classified.append(classify(data, tree).keys()[0])


def classifyBinaryData(tree):
	for data in documentMatrix:
		classifiedBinary.append(classify(data, tree).keys()[0])

def testDTree(path, modelFile):
	trees = readTreeModelFile(modelFile)
	bow = trees[2]
	tree = trees[0]
	treeBinary = trees[1]
	addTestData(bow, path)
	classifyData(tree)
	classifyBinaryData(treeBinary)
	counter = 0
	counter2 = 0
	for i in range(len(documentMatrix)):
		if classified[i] == documentMatrix[i][-1]:
			counter+=1
		else:
			counter2+=1
	print "Accuracy for Frequency" + str((counter/(len(documentMatrix) * 1.0) * 100))

	counter3 = 0
	counter4 = 0
	for i in range(len(documentBinaryMatrix)):
		if classifiedBinary[i] == documentBinaryMatrix[i][-1]:
			counter3+=1
		else:
			counter4+=1
	print "Accuracy for Binary" + str((counter3/(len(documentBinaryMatrix) * 1.0) * 100))
