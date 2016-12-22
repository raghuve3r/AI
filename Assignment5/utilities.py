'''
This file contains the utility functions that can be used through out the assignment.
'''
import os

def readFile(fileName):
	file = open(fileName, 'r')
	lines = file.readlines()
	file.close()
	return lines


def convertToRGB(fileName):
	RGBList = dict()
	ctr = 0
	contents = readFile(fileName)
	for eachLine in contents:
		rgbValues = ()
		imageVector = eachLine.split(' ')
		for i in range(2, len(imageVector)):
			rgbValues = rgbValues + (int(imageVector[i]), )
		RGBList[ctr] = (int(imageVector[1]), rgbValues, imageVector[0])
		ctr += 1
	return RGBList

def findIntensity(pixel):
	return (0.2989 * pixel[0]) + (0.5870 * pixel[1]) + (0.1140 * pixel[2])


def outputMatrix(valueDict, fileName):
	print 'The Accuracy of the classifier is ' + str(((valueDict[0][0] + valueDict[90][1] + valueDict[180][2] +
	                                                   valueDict[270][3]) / ((sum(valueDict[0]) + sum(
		valueDict[90]) + sum(valueDict[180]) + sum(valueDict[270])) * 1.0)) * 100.0) + '\n'
	print 'The Confusion Matrix looks like this\n'
	for val in valueDict.values():
		for item in val:
			print '{:4}'.format(item),
		print ''

def writeFile(list1, fileName):
	file = open(fileName, 'wb')
	for eachRow in list1:
		file.write(eachRow)
		file.write(os.linesep)
	file.close()