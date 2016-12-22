import numpy as np

probabilityMatrix = np.array([[0.5,0.6,0.7,0.8],[0.1,0.8,0.7,0.9],[0.1,0.2,0.3,0.1],
                     [0.1, 0.2, 0.3, 0.1], [0.1,0.2,0.3,0.1], [0.1,0.2,0.1,0.1],
                     [0.1, 0.2, 0.2, 0.1], [0.1,0.2,0.4,0.1]])



def calcSamples(colNo, topEdgeVals):
    for eachVal in topEdgeVals:
        topEdgeVals1 = []
        for i in range(len(probabilityMatrix)):
            topEdgeVals1.append(i)
            print eachVal, probabilityMatrix[i][colNo]
    return topEdgeVals1


returnedVal = calcSamples(1, [1,2])
print returnedVal

for i in range(2,4):
    returnedVal = calcSamples(i, returnedVal[:2])

a = [(1, 10),(2, 6)]

a.sort(key=lambda tup: tup[1])

print a

print type(a[0]) is tuple

a = (1,2)
b = (3,4)
c = (5,6)

for i in range(3):
    tuple1 = (a,)

print tuple1

print len(probabilityMatrix) - int(round(0.65 * len(probabilityMatrix)))

print int(round(0.2 * len(probabilityMatrix)))


probabilityMatrix = probabilityMatrix[int(round(0.2 * len(probabilityMatrix))):]

print probabilityMatrix

a = [1,2,4,5,6]
a.reverse()
print a