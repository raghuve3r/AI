from heuristics import *

def drawRidge(rowNo, colNo):
    try:
        topRidgeVals = []
        for i in range(rowNo - 5, rowNo + 5):
            topRidgeVals.append(
                (i, formulaToCalculate(modifiedProbStrength[i][colNo + 1], len(modifiedProbStrength), abs(rowNo - i))
                 , modifiedProbStrength[i][colNo + 1]))
        return topRidgeVals
    except:
        j = 1


def drawRidgeNeg(rowNo, colNo):
    try:
        topRidgeVals = []
        for i in range(rowNo - 5, rowNo + 5):
            topRidgeVals.append(
                (i, formulaToCalculate(modifiedProbStrength[i][colNo - 1], len(modifiedProbStrength), abs(rowNo - i))
                 , modifiedProbStrength[i][colNo - 1]))
        return topRidgeVals
    except:
        j = 1