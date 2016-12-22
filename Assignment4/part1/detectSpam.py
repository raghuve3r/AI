'''
This file is to detect whether the given Email is a spam or not
'''

import os
import re
import math
from collections import Counter
from heapq import nsmallest
import pickle

spamWords = dict()
nonSpamWords = dict()

binarySpam = dict()
binaryNonSpam = dict()

topTenSpam = dict()
topTenNotSpam = dict()

topTenBSpam = dict()
topTenBNotSpam = dict()

k = 1.5

def readPickleFile(fileName):
   with open(fileName, 'rb') as file:
      return pickle.load(file)


def readModel(fileName):
   file = readPickleFile(fileName)
   numOfSpans = file[0]
   numOfNonSpams = file[1]

   for line in file[2]:
      values = line.split(' ')
      if values[3].strip() == 's':
         spamWords[values[0]] = float(values[1])
         binarySpam[values[0]] = float(values[2])
      else:
         nonSpamWords[values[0]] = float(values[1])
         binaryNonSpam[values[0]] = float(values[2])

   return numOfSpans, numOfNonSpams

def readFile(fileName):
   file = open(fileName, 'r')
   lines = file.readlines()
   file.close()
   return 0,lines

def updateConfusionMatrix(mode, m, confMatrix):
   if mode == 'spam':
      if m == 'spam':
         confMatrix['tp'] += 1
      else:
         confMatrix['fn'] += 1
   else:
      if m == 'spam':
         confMatrix['fp'] += 1
      else:
         confMatrix['tn'] += 1


def cleanHtml(raw_html):
   cleanr = re.compile('<.*?>')
   cleantext = re.sub(cleanr, '', raw_html)
   removeLines = re.compile('\n')
   cleantext = re.sub(removeLines, '', cleantext)
   removeSpecialCases = re.compile('[\\]x[0-9][0-9]')
   cleantext1 = re.sub(removeSpecialCases, '', cleantext)
   return cleantext1


def checkSpam(lines, mode, confusionMatrix, confusionMatrixB, numOfSpams, numOfNonSpams):
   wc = Counter()
   spamProbability = 0
   bSpamProbability = 0
   nonSpamProbability = 0
   bNonSpamProbability = 0
   for line in lines:
      word = line.split(' ')
      for w in word:
         wc[w] += 1

   for k, v in wc.iteritems():
      if k in spamWords:
         spamProbability += math.log(float(v) / float(spamWords[k]))
         bSpamProbability += math.log(float(v) / float(binarySpam[k]))
      else:
         spamProbability += math.log(float(1) / 2)
         bSpamProbability += 0

      if k in nonSpamWords:
         nonSpamProbability += math.log(float(v) / float(nonSpamWords[k]))
         bNonSpamProbability += math.log(float(v) / float(binaryNonSpam[k]))
      else:
         nonSpamProbability += math.log(float(1) / 2)
         bNonSpamProbability += 0

   spamProbability = spamProbability * numOfSpams
   nonSpamProbability = nonSpamProbability * numOfNonSpams
   bSpamProbability = bSpamProbability * numOfSpams
   bNonSpamProbability = bNonSpamProbability * numOfNonSpams
   Q1 = spamProbability / nonSpamProbability


   Q2 = bSpamProbability / bNonSpamProbability if bNonSpamProbability != 0.0 else 0
   m = 'spam' if Q1 > 0.84 else 'nonspam'

   updateConfusionMatrix(mode, m, confusionMatrix)

   m = 'spam' if Q2 > 0.83 else 'nonspam'

   updateConfusionMatrix(mode, m, confusionMatrixB)

def printTopTen(words):
	ctr1 = 0
	for word, val in nsmallest(10, words.iteritems(), key=lambda (k, v): (-v, k)):
		ctr1 += 1
		print ctr1, '.', word



def readTestData(directory, modelFile):

   confusionMatrix = {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}
   confusionMatrixB = {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}
   numOfSpans, numOfNonSpams = readModel(modelFile)

   for i in range(0, 2):
      spamCheck = 'spam' if i == 0 else 'nonspam'
      spamPath = directory +'/spam' if i == 0 else directory + '/notspam'
      for path, dirs, files in os.walk(spamPath):
         for filename in files:
            if filename != 'cmds':
               x = os.path.join(path, filename)
               index, Lines = readFile(x)
               checkSpam(Lines[index + 1:len(Lines)], spamCheck, confusionMatrix, confusionMatrixB, numOfSpans,
                         numOfNonSpams)

   accuracy = ((confusionMatrix['tp'] + confusionMatrix['tn']) / (sum(confusionMatrix.values()) * 1.0)) * 100.0

   accuracyB = ((confusionMatrixB['tp'] + confusionMatrixB['tn']) / (sum(confusionMatrixB.values()) * 1.0)) * 100.0


   print 'Testing is done. Below are the results\n'

   print '\nThe total accuracy taking into account word frequency is ' + str(accuracy) + '%'

   print '\nTop ten words associated with spam:\n'
   printTopTen(spamWords)

   print '\nTop ten words least associated with not spam:\n'
   printTopTen(nonSpamWords)

   print '\nThe total accuracy for Binary is ' + str(accuracyB) + '%'

   print '\nTop ten words associated with spam(Binary):\n'
   printTopTen(binarySpam)

   print '\nTop ten words least associated with not spam(Binary):\n'
   printTopTen(binaryNonSpam)

