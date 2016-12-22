#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#1) Formulation and description:
#        a) The simple model does not account the previous or the subsequent states. Hence we maximise the edge strength on each column and paint the image.
#
#        b) This method uses MCMC technique and HMMs. It used Formula being, (probScore * numberofRows) / (1 + rowDiff).
#
#        c) Based on the User feedback, We make use of the same technique as explained above and instead of searching for the column, It seacrhes
#           +10 and -10 rows and goes on drawing the ridge.

#2) Description of how the program works:
#        a) We move through each column and find out the row value which has the highest value.
#           This row value is then appended to a list 'ridge'. The final 'ridge' will have a list of all the row values, which is then passed to the draw_edge() function.
#
#        b) The program selects the top Edge Values and randomly selects a point and compares
#           with each pixel in the next column. The program has been modeled with probability distribution and makes use of a formula defined by us to calculate probability score. 
#           We then seelct top 20 scores and checks with next column and so on. 
#
#        c) Based on the User feedback, the program checks for +10 and -10 rows and the next or previous column.
#
#

#3) Assumptions:
#        a) We assume that for each column the row with the highest value as the point to draw the line.
#
#        b) Ridgeline won't appear at the bottom 20%. Functions can be found in heuristics.py file.
#
#        c) Same as the previous problem.
#

from PIL import Image
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
from heuristics import *
from copy import deepcopy

import sys

# calculate "Edge strength map" of an image
#
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return filtered_y**2

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_edge(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( max(y-thickness/2, 0), min(y+thickness/2, image.size[1]-1 ) ):
            image.putpixel((x, t), color)
    return image

# main program
#
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]
gt_row = int(gt_row)
gt_col = int(gt_col)

# load in image
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
edgeStrength = deepcopy(edge_strength)
modifiedEdgeStrength = removeUseless(edgeStrength, int(len(edgeStrength) - round(0.2 * len(edgeStrength))))
#part1
row_index = edge_strength.argmax(axis=0)
imsave('edges.jpg', edge_strength)
#part-2
minParameters = []
topEdgeVals = []

for i in range(len(modifiedEdgeStrength[0])):
    colState = []
    for eachrow in modifiedEdgeStrength:
        colState.append(eachrow[i])
    minMaxEdgeWeight, topVals = lowerRows(colState)
    minParameters.append(minMaxEdgeWeight)
    topEdgeVals.append(topVals)

for i in range(len(topEdgeVals)):
    colState = []
    for eachrow in modifiedEdgeStrength:
        colState.append(eachrow[i])

totalMatrix = []
for i in range(len(modifiedEdgeStrength[0])):
    eachCol = []
    columnValues = []
    for eachrow in modifiedEdgeStrength:
        columnValues.append(eachrow[i])
    for j in range(len(columnValues)):
        eachCol.append(columnValues[j]/sum(columnValues))
    totalMatrix.append(eachCol)

probabilityMatrix = transpose(totalMatrix)
modifiedProbStrength = removeUseless(probabilityMatrix, int(len(probabilityMatrix) - round(0.2 * len(probabilityMatrix))))


def calcSamples(colNo, topEdgeVals):
    for eachVal in topEdgeVals:
        topEdgeVals1 = []
        for i in range(len(modifiedProbStrength)):
            if type(eachVal) is tuple:
                topEdgeVals1.append(
                    (i, formulaToCalculate(modifiedProbStrength[i][colNo], len(modifiedEdgeStrength), abs(eachVal[0] - i)), modifiedProbStrength[i][colNo]))
            else:
                topEdgeVals1.append(
                    (i, formulaToCalculate(modifiedProbStrength[i][colNo], len(modifiedEdgeStrength), abs(eachVal - i)), modifiedProbStrength[i][colNo]))
    return topEdgeVals1

returnedVal = calcSamples(1, topEdgeVals[0])

def bestReturnedVals(values):
    values.sort(key=lambda tup: tup[1])
    return values[-10:]

T = 10

allPossibleRidges = []

for t in range(1, T):
    finalRidgeList = []
    probCounter = []
    finalRidgeList.append(topEdgeVals[0][0])
    probCounter.append(0)
    if t != 1:
        returnedVal = calcSamples(1, topEdgeVals[0])
    for i in range(2, len(modifiedEdgeStrength[0])):
        bestVals = bestReturnedVals(returnedVal)
        returnedVal = calcSamples(i, bestVals)
        finalRidgeList.append(bestVals[-1][0])
        probCounter.append(bestVals[-1][2])

    allPossibleRidges.append((finalRidgeList, sum(probCounter)))

allPossibleRidges.sort(key=lambda tup: tup[1])
finalRidgeList = allPossibleRidges[-1][0]

#Part-3

def drawRidge(rowNo, colNo):
    try:
        topRidgeVals = []
        for i in range(rowNo - 9, rowNo + 10):
            topRidgeVals.append(
                (i, formulaToCalculate(modifiedProbStrength[i][colNo + 1], len(modifiedProbStrength), abs(rowNo - i))
                 , modifiedProbStrength[i][colNo + 1]))
        return topRidgeVals
    except:
        j = 1


def drawRidgeNeg(rowNo, colNo):
    try:
        topRidgeVals = []
        for i in range(rowNo - 9, rowNo + 10):
            topRidgeVals.append(
                (i, formulaToCalculate(modifiedProbStrength[i][colNo - 1], len(modifiedProbStrength), abs(rowNo - i))
                 , modifiedProbStrength[i][colNo - 1]))
        return topRidgeVals
    except:
        j = 1

finalRidgeListUserDef = []
probCounterUserDef = []
retVal = drawRidgeNeg(gt_row, gt_col)
for i in range(gt_col - 1, -1, -1):
    bestVal = bestReturnedVals(retVal)
    retVal = drawRidgeNeg(bestVal[-1][0], i)
    finalRidgeListUserDef.append(bestVal[-1][0])
    probCounterUserDef.append(bestVal[-1][2])

finalRidgeListUserDef.reverse()
finalRidgeListUserDef.append(gt_row)
probCounterUserDef.append(0)

for i in range(gt_col+1, len(modifiedEdgeStrength[0])):
    if i == gt_col + 1:
        returnedVal = drawRidge(gt_row, i)
        best1Val = bestReturnedVals(returnedVal)
    else:
        best1Val = bestReturnedVals(returnedVal)
        returnedVal = drawRidge(best1Val[-1][0], i)
    finalRidgeListUserDef.append(best1Val[-1][0])
    probCounterUserDef.append(best1Val[-1][2])


# You'll need to add code here to figure out the results! For now,
# just create a horizontal centered line.
imsave(output_filename, draw_edge(input_image, row_index, (255, 0, 0), 6))
imsave(output_filename, draw_edge(input_image, finalRidgeList, (0, 0, 255), 4))
imsave(output_filename, draw_edge(input_image, finalRidgeListUserDef, (0, 255, 0), 2))
