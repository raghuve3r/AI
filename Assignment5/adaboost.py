'''
We are implementing decision stumps using adaboost.

Decision stumps are nothing but decision tree with a single root node and two leaf nodes.

The given dataset had 192 features, which consisted of 64 pixels of RGB.
We calculated the intensity for each pixel and converted it into a single composite value,
thereby reducing the features to 64 from 192.

We are building 4 ensemble classifiers here, one for each orientation.

This dataset is then passed onto the ensemble method along with the number of stumps to be built,
the appropriate ensemble for an orientation, weight vector and the number of misclassifications in the dataset.

This ensemble method in turn calls calculateBestSplit method for 'number of stumps' times.
This will result to building of specified number of stumps.
But behind the scenes we are building 4 times the number of stumps specified
because we are building a stump for each orientation.

In calculateBestSplit method we choose two columns randomly to split our data.
We check if the value in one column is greater than the value in other column,
if the condition is true, then we assume the class label to be of a certain orientation.
If the predicted class value does not match the actual class label then we increment the error count.
After we have scanned through the entire dataset, we again go through the entire dataset to increment our weight vector.
We give a high weightage to the records which were misclassified.

The error weight is calculated using the formula:
New Weight = Old weight * error rate/ (1 - error rate)

After updating the weights vector we go on to calculate the alpha of that stump:
alpha = (1 - error rate/ error rate) * 100000

In the end we will have the alpha for that stump and the attribute at which it has to split,
along with the count of misclassification.

After our training phase we will end up decision stumps equalling the number specified,
pair of attributes for each stump respectively and alpha values for each stump.

In our testing phase we will pass each record through ensembles of 4 different orientations.
Each ensemble will have specified number of stumps.
Each stump will try to split the test record based on the attribute selected for that stump.
If the condition is satisfied then the alpha value is multiplied with +1 else it is multiplied by -1.
We then take the summation of the values calculated in the previous step. We do this for all 4 ensembles.
We take the maximum out of those values and check which ensemble got the maximum value.
We classify the test record as belonging to the class for which the ensemble voted.
'''





from utilities import *
import random
import operator
import os






def calculateBestSplit(datatset, degree, weight, ensemble, error):
    dataLength = len(datatset[0][1])
    x, y = random.sample(set(list(range(dataLength))), 2)
    maxWeight = max(weight)
    er = max(weight)
    if x != y:
        counter = 0
        tempSuccess = 0
        tempError = 0
        for records in datatset.values():
            tempDegree = 1
            if records[1][x] > records[1][y]:
                tempDegree = degree
            if tempDegree == records[0]:
                tempSuccess += 1
            else:
                tempError += 1
            counter += 1
        counterNew = 0
        error = tempError
        errorWeight = float(tempError) / len(datatset)
        errorWeight = (er * errorWeight) / (1 - errorWeight)
        for records in datatset.values():
            tempDegree = 1
            if weight[counterNew] == maxWeight:
                if records[1][x] > records[1][y]:
                    tempDegree = degree
                if tempDegree == records[0]:
                    weight[counterNew] = errorWeight
            counterNew += 1
        bestAtt1 = x
        bestAtt2 = y
        if (bestAtt1, bestAtt2) not in ensemble:
            alpha = float(1 - (float(error) / len(datatset))) / (float(error) / len(datatset))
            alpha = alpha * 100000
            l = []
            l.append(alpha)
            l.append((x, y))
            ensemble.append(l)


    return ensemble, error



def ensemble(dataset, numOfStumps, degree, weight, error):

    ensemble = []
    e = error
    for i in range(numOfStumps):
        ensemble, e = calculateBestSplit(dataset,degree,weight,ensemble, e)
        sumOfWeights = sum(weight)
        weight = [float(j)/sumOfWeights for j in weight]
    return ensemble



def testing(e0,e1,e2,e3,dataset):
    correctness = 0
    counterDict1 = {0: [0, 0, 0, 0], 90: [0, 0, 0, 0], 180: [0, 0, 0, 0], 270: [0, 0, 0, 0]}
    indexDict = {0: 0, 90: 1, 180: 2, 270: 3}
    output = []
    for record in dataset.values():
        counterDict = {'counter0':0, 'counter1':0, 'counter2':0, 'counter3':0}
        for i in range(len(e0)):
            val = e0[i][0]
            att = e0[i][1]
            x = att[0]
            y = att[1]
            if record[1][x] > record[1][y]:
                counterDict['counter0'] += val * 1
            else:
                counterDict['counter0'] += val * -1
        for i in range(len(e1)):
            val = e1[i][0]
            att = e1[i][1]
            x = att[0]
            y = att[1]
            if record[1][x] > record[1][y]:
                counterDict['counter1'] += val * 1
            else:
                counterDict['counter1'] += val * -1
        for i in range(len(e2)):
            val = e2[i][0]
            att = e2[i][1]
            x = att[0]
            y = att[1]
            if record[1][x] > record[1][y]:
                counterDict['counter2'] += val * 1
            else:
                counterDict['counter2'] += val * -1
        for i in range(len(e3)):
            val = e3[i][0]
            att = e3[i][1]
            x = att[0]
            y = att[1]
            if record[1][x] > record[1][y]:
                counterDict['counter3'] += val * 1
            else:
                counterDict['counter3'] += val * -1

        maximumScore = sorted(counterDict.iteritems(), key=operator.itemgetter(1), reverse=True)
        vote = maximumScore[0][0]
        if vote == 'counter0':
            c = 0
        elif vote == 'counter1':
            c = 90
        elif vote == 'counter2':
            c =180
        else:
            c =270
        if c == int(record[0]):
            correctness += 1

        output.append(str(record[2]) + ' ' + str(c))

        if int(record[0]) == 0:
            if int(record[0]) == c:
                counterDict1[0][0] += 1
            else:
                counterDict1[0][indexDict[c]] += 1

        elif int(record[0]) == 90:
            if int(record[0]) == c:
                counterDict1[90][1] += 1
            else:
                counterDict1[90][indexDict[c]] += 1

        elif int(record[0]) == 180:
            if int(record[0]) == c:
                counterDict1[180][2] += 1
            else:
                counterDict1[180][indexDict[c]] += 1

        else:
            if int(record[0]) == c:
                counterDict1[270][3] += 1
            else:
                counterDict1[270][indexDict[c]] += 1
    outputMatrix(counterDict1,'adaboost_confusion.txt')
    writeFile(output, 'adaboost_output.txt')


def adaboost(trainTest, testSet, stumps, model):
    e0, e1, e2, e3 = 0, 0, 0, 0
    testDict = convertToRGB(testSet)
    trainingSet = convertToRGB(trainTest)
    orientation = [0,90,180,270]
    points = float(1)/len(trainingSet)
    for i in orientation:
        weight = [points] * len(trainingSet)
        error = len(trainingSet)
        e = ensemble(trainingSet,int(stumps),i, weight, error)
        if i == 0:
            e0 = e
        elif i == 90:
            e1 = e
        elif i == 180:
            e2 = e
        else:
            e3 = e
    testing(e0, e1, e2, e3, testDict)
