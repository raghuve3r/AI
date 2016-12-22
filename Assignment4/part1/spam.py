from sys import argv

import buildModel
import detectSpam
import dTreeTrain
import dTreeTest

if len(argv) != 5:
    print("USAGE: Mode technique directory model_file")
    exit(1)

mode = argv[1]
technique = argv[2]
directory = argv[3].rstrip('/')
modelFile = argv[4]

if technique == "bayes":
    if mode == "train":
        buildModel.readTrainData(directory, modelFile)
    elif mode == "test":
        detectSpam.readTestData(directory, modelFile)
    else:
        print("Invalid parameter")
        exit(1)
elif technique == "dt":
    if mode == "train":
        dTreeTrain.trainDTree(directory, modelFile)
    elif mode == "test":
        dTreeTest.testDTree(directory, modelFile)
    else:
        print("Invalid parameter")
        exit(1)