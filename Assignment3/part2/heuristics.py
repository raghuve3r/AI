import numpy as np

def lowerRows(edgeStrength):
    array = np.asarray(edgeStrength)
    topValues = array.argsort()[-20:]
    return min(topValues), topValues

def calcDist(a, b):
    return np.linalg.norm(a - b)

def formulaToCalculate(probScore, numberofRows, rowDiff):
    return (probScore * numberofRows) / (1 + rowDiff)

def removeUseless(matrix, limit):
    return matrix[:limit]

