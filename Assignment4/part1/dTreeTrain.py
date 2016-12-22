from utilities import *
import os
import math
from stopWords import *
from collections import Counter
import pickle


documentMatrix = []
binaryDocumentMatrix = []
array1 = []

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

def divideTree(rows, column, value):
    tree1 = [row for row in rows if row[column] >= value]
    tree2 = [row for row in rows if not row[column] >= value]
    return (tree1, tree2)

def createBinaryMatrix(lines, mode, bow):
	array = []
	wd = []
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
	binaryDocumentMatrix.append(array)

def addTrainingData(directory, bow):
	counter = 0
	for i in range(0,2):
		folderpath = directory + '/spam' if i == 0 else directory + '/notspam'
		for path, dirs, files in os.walk(folderpath):
			for filename in files:
				counter += 1
				if filename != 'cmds':
					x = os.path.join(path, filename)
					Lines = readFile(x)
					createMatrix(Lines, 'spam', bow) if i == 0 else createMatrix(Lines, 'notspam', bow)
					createBinaryMatrix(Lines, 'spam', bow) if i == 0 else createBinaryMatrix(Lines, 'notspam', bow)

def classCount(rows):
   results = {}
   for row in rows:
      r = row[len(row)-1]
      if r not in results:
		  results[r] = 0
      results[r] += 1
   return results

def calculateEntropy(rows):
   results = classCount(rows)
   ent = 0.0
   for r in results.keys():
      p = float(results[r])/len(rows)
      ent = ent-p*math.log(p,2)
   return ent

def printtree(tree,indent=''):
    if tree.results != None:
        print str(tree.results)
    else:
        if tree.name != None:
            print tree.name
        print indent +'Right'+' ', printtree(tree.right,indent+'  ')
        print indent +'Left' +' ', printtree(tree.left,indent+'  ')

def calculateInfoGain(current_score, set1, set2, param):
	p = len(set1)/param
	gain = current_score - p * calculateEntropy(set1) - (1 - p) * calculateEntropy(set2)
	return p, gain

def buildtree(rows, bow):
	if len(rows) == 0:
		return decisionTree()
	current_score = calculateEntropy(rows)
	infoGain = 0.0
	splitAttribute = None
	split = None
	noOfColumns = len(rows[0]) - 1
	for col in range(noOfColumns):
		cols = {}
		for row in rows:
			cols[row[col]] = 1
		for value in cols.keys():
			(tree1, tree2) = divideTree(rows, col, value)
			p,gain = calculateInfoGain(current_score, tree1, tree2, len(rows))
			if gain > infoGain and len(tree1) > 0 and len(tree2) > 0:
				infoGain = gain
				splitAttribute = (col, value)
				split = (tree1, tree2)
	if infoGain > 0:
		trueBranch = buildtree(split[0], bow)
		falseBranch = buildtree(split[1], bow)
		return decisionTree(col=splitAttribute[0], value=splitAttribute[1], right=trueBranch, left=falseBranch, name=bow[splitAttribute[0]])
	else:
		return decisionTree(results=classCount(rows))

def trainDTree(path, modelFile):
	bow = makeBOW(path)
	addTrainingData(path, bow)
	tree = buildtree(documentMatrix, bow)
	treeBinary = buildtree(binaryDocumentMatrix, bow)
	array1.append(tree)
	array1.append(treeBinary)
	array1.append(bow)
	printtree(tree)
	print "Binary"
	printtree(treeBinary)
	with open(modelFile, 'wb') as file:
		pickle.dump(array1, file)
'''


if __name__ == '__main__':
	bow = makeBOW('train')
	addTrainingData('train')
	tree = buildtree(documentMatrix)
	treeBinary = buildtree(binaryDocumentMatrix)
	with open('treeModelFile', 'wb') as file:
		pickle.dump(tree, file)
	with open('treeBinaryModelFile', 'wb') as file:
		pickle.dump(treeBinary, file)
	printtree(tree)
	print "Binary"
	printtree(treeBinary)
'''