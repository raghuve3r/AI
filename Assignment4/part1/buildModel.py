from utilities import *
from detectSpam import *
from stopWords import *
from collections import Counter
import pickle

spamWordCount = Counter()
binarySpamWordCount = Counter()
nonspamWordCount = Counter()
binaryNonSpamWordCount = Counter()

def readFile(fileName):
    file = open(fileName, 'r')
    lines = file.readlines()
    file.close()
    return 0,lines

def addToArray(lines, mode):
    for line in lines:
        word = line.split(' ')
        words = []
        for w in word:
            w = w.lower()
            w = ''.join(e for e in w if e.isalnum())
            if not 'nbsp' in w and w not in stopWords and w.isalpha():
                if mode == 'spam':
                    spamWordCount[w] += 1
                    if w not in words:
                        words.append(w)
                        binarySpamWordCount[w] += 1
                else:
                    nonspamWordCount[w] += 1
                    if w not in words:
                        words.append(w)
                        binaryNonSpamWordCount[w] += 1


def writeModelFile(modelFileList, modelFile):
    with open(modelFile, 'wb') as file:
        pickle.dump(modelFileList, file)


def readTrainData(directory, modelFile):
    modelFileList = []
    allWords = []

    noOfSpamFiles = 0
    noOfNonSpamFiles = 0
    for i in range(0, 2):
        folderpath = directory +'/spam' if i == 0 else directory + '/notspam'
        for path, dirs, files in os.walk(folderpath):
            if folderpath == 'train/spam':
                noOfSpamFiles += len(files) - 1
            else:
                noOfNonSpamFiles += len(files) - 1

            for filename in files:
                if filename != 'cmds':
                    x = os.path.join(path, filename)
                    index, Lines = readFile(x)
                    addToArray(Lines, 'spam') if i == 0 else addToArray(Lines, 'nonspam')

    numOfSpams = noOfSpamFiles / ((noOfSpamFiles + noOfNonSpamFiles) * 1.0)
    numOfNonSpams = noOfNonSpamFiles / ((noOfSpamFiles + noOfNonSpamFiles) * 1.0)

    modelFileList.append(numOfSpams)
    modelFileList.append(numOfNonSpams)

    for eachword in spamWordCount:
        allWords.append((eachword.strip() + ' ' + str(spamWordCount[eachword]) + ' ' + str(binarySpamWordCount[eachword]) + ' ' + 's'))

    for eachword in nonspamWordCount:
        allWords.append((eachword.strip() + ' ' + str(nonspamWordCount[eachword]) + ' ' + str(binaryNonSpamWordCount[eachword]) + ' ' + 'ns'))

    modelFileList.append(allWords)
    writeModelFile(modelFileList, modelFile)
    print 'Training is done. Please run Test to see the accuracy of this model.'
