'''
KNN is a classifier which classifies based on the Euclidean distance between the test set instance and each training set instaces.

The Professor has asked us to implement Nearest Neighbor which means the value of K = 1. I tried with multiple values of K and this
program worked better with k = 10 with an accuracy of 72.33%, whereas, for k = 1, the accuracy is 67.23%.

We've written a program that takes into account the voting as well just in case the AI's want to try with different values.

def convertToPixelVals(dataList): Converts the data into a dictionary with key starting from 0 to lenth of dataset and last value being it's orientation

def calcDistance(list1, list2): calculates the Eucilidean distance between two vectors.

def calcNeighborProximity(testRow, trainDict, k=1): Returns the trainset with least Euclidean distance.

def getVoting(neighbors): Based on the value of k, it calculates how many times each class has occured and takes into account
the voting.

def getAccuracy(testDict, predictions): Returns a dictionary which has confusion matrix.
'''


from utilities import *
import math
import operator
#Tuple will be of type {Key : ([pixel vals...], orientation)}

def convertToPixelVals(dataList):
	pixelValue = dict()
	ctr = 0
	for eachRow in dataList:
		values = eachRow.strip().split(' ')
		pixelValue[ctr] = (map(int, values[2:len(values)]), int(values[1]), values[0])
		ctr += 1
	return pixelValue


def calcDistance(list1, list2):
	distance = [(ctr1 - ctr2) ** 2 for ctr1, ctr2 in zip(list1, list2)]
	return math.sqrt(sum(distance))


def calcNeighborProximity(testRow, trainDict, k=1):
	distanceFromEach = list()
	for vals in trainDict.values():
		distanceFromEach.append((vals[0], vals[1], calcDistance(testRow[0], vals[0])))
	distanceFromEach.sort(key=lambda tup: tup[2])
	return distanceFromEach[:k]


def getVoting(neighbors):
	votingDict = dict()
	for neighbor in neighbors:
		if neighbor[1] in votingDict.keys():
			votingDict[neighbor[1]] += 1
		else:
			votingDict[neighbor[1]] = 1
	sortedNeighbors = sorted(votingDict.iteritems(), key=operator.itemgetter(1), reverse=True)
	return sortedNeighbors[0][0]

def getAccuracy(testDict, predictions):
	counterDict = {0:[0, 0, 0, 0], 90:[0, 0, 0, 0], 180:[0, 0, 0, 0], 270:[0, 0, 0, 0]}
	indexDict = {0:0, 90:1, 180:2, 270:3}
	ctr = 0
	predictionOutput = []

	for val in testDict.values():
		predictionOutput.append(val[2] + ' ' + str(predictions[ctr]))
		if val[1] == 0:
			if val[1] == predictions[ctr]:
				counterDict[0][0] += 1
			else:
				counterDict[0][indexDict[predictions[ctr]]] += 1

		elif val[1] == 90:
			if val[1] == predictions[ctr]:
				counterDict[90][1] += 1
			else:
				counterDict[90][indexDict[predictions[ctr]]] += 1

		elif val[1] == 180:
			if val[1] == predictions[ctr]:
				counterDict[180][2] += 1
			else:
				counterDict[180][indexDict[predictions[ctr]]] += 1

		else:
			if val[1] == predictions[ctr]:
				counterDict[270][3] += 1
			else:
				counterDict[270][indexDict[predictions[ctr]]] += 1

		ctr += 1

	return counterDict, predictionOutput


def nearest(trainFile, testFile, count, modelFile):
	trainList = readFile(trainFile)
	testList = readFile(testFile)
	testDict = convertToPixelVals(testList)
	trainDict = convertToPixelVals(trainList)
	predictions = list()
	for val in testDict.values():
		topNeighbors = calcNeighborProximity(val, trainDict)
		predictedClass = getVoting(topNeighbors)
		predictions.append(predictedClass)

	counterDict, listForOutput = getAccuracy(testDict, predictions)
	outputMatrix(counterDict, 'nearest_output.txt')
	writeFile(listForOutput, 'nearest_output.txt')
