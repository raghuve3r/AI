from sys import argv
import nnet
import nearestNeighbor
import adaboost as boost

algo_dict = {
    'nnet': nnet.neural_net,
    'nearest': nearestNeighbor.nearest,
    'best': nnet.neural_net,
	'adaboost': boost.adaboost
}

if len(argv) < 4:
    print("USAGE: train_file test_file algo [count]")
    exit(1)

train_file = argv[1]
test_file = argv[2]
algo = argv[3]
count = 0
if algo == 'best':
    model_file = False
    count = 64
    if len(argv) > 4:
        model_file = argv[4]

else:
    try:
        count = argv[4]
    except Exception:
        count = 0
    try:
        model_file = argv[5]
    except Exception:
        model_file = False

try:
    algo_dict[algo](train_file,test_file,count,model_file)
except KeyError:
    print("Invalid Algorithm %s. Please check again" %algo)


