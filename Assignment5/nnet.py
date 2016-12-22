import os
import pickle
from collections import Counter
from collections import defaultdict
from math import e, log
from random import gauss, sample
from utilities import writeFile


"""
(1) This program builds a two layer neural network with the given number of nodes in the hidden layer. The model
file is read line by line, information is parsed and fed as the input to the network. A softmax function is
applied to the output of the output nodes. The network is trained based on the back propagation algorithm using
gradient descent where the delta is calculated and propagated back till the input layer of the network. The
training stops once it reaches a low error rate. Finally, the network is tested by reading values from the test
file and the confusion matrix and accuracy is displayed.

(2) The method neural_net(args...) can be seen as the starting point of this program where it takes the train and
test files, the hidden node count and an optional file_name to either read the model from or store the trained model
into. It processes the training file and puts it into 'examples' dictionary, creates an initial Network object and
starts learning. The learn method randomly picks samples from examples and starts propagating into the network.
 Errors are corrected while back propagation. There is also an initial expectation set which is used as the stopping
 criteria for the training. The expectation is decreased after a while if the network fails to converge.
    The trained network is tested against the images in the testing set and the confusion matrix and the accuracies
    are displayed.

(3) The alpha is set to be 1/length of the training set.
I used the smoothing approximation of ReLu as my activation function
The output is fed into softmax function so that we can pick the majority among the output nodes.
The expectation is initially set to be 85% right predictions and it is adjusted as the iteration goes.
"""

alpha = 0.00001
orient = [0, 90, 180, 270]


class Pixel:
    """
    Holds the r,g,b values of a pixel and its grayscale intensity.
    """

    def __init__(self, r, g, b):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.intensity = self.find_intensity()

    # Convert the rgb values into a grayscale intensity. Constant values taken from:
    # http://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
    # Many other links also suggested the same value.
    def find_intensity(self):
        return (0.2989 * self.r) + (0.5870 * self.g) + (0.1140 * self.b)


class Network:
    """
    A network of neurons with supporting attributes like weight node numbers and count at each layer.
    """

    def __init__(self, input_node_count, hidden_node_count, output_node_count):
        self.input_node_count = int(input_node_count)
        self.hidden_node_count = int(hidden_node_count)
        self.output_node_count = int(output_node_count)
        self.weights = self.assign_random_weights()
        self.hidden_end = self.input_node_count + self.hidden_node_count
        self.output_end = self.hidden_end + self.output_node_count
        self.L = 3

    def assign_random_weights(self):
        weights = defaultdict(defaultdict)
        hidden_start = self.input_node_count
        hidden_end = hidden_start + self.hidden_node_count
        output_start = hidden_end
        output_end = output_start + self.output_node_count
        for i in range(self.input_node_count):
            for j in range(hidden_start, hidden_end):
                for k in range(output_start, output_end):
                    weights[j][k] = self.get_initial_weight()
                weights[i][j] = self.get_initial_weight()

        return weights

    @staticmethod
    def get_initial_weight():
        return gauss(0.001, 0.01)


class Propagator:
    """
    Holds the data structures that help propagating the values in a neural
    network. Supports both forward and backward propagation
    """

    def __init__(self, ground_truth):
        self.y = get_orientation_list(ground_truth)
        self.a = defaultdict()
        self.in_vec = defaultdict()
        self.delta = defaultdict()
        self.soft_max_vals = []

    def __add__(self, other):
        self.a = Propagator.add_two_dict(self.a, other.a)
        self.in_vec = Propagator.add_two_dict(self.in_vec, other.in_vec)
        self.delta = Propagator.add_two_dict(self.delta, other.delta)

    @staticmethod
    def add_two_dict(x, y):
        return {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}


class Result:
    """
    Has the confusion matrix, images classified correctly and total number of images tested against.
    Also handles displaying the results on the console.
    Reused my Assignment 4 implementation.
    """

    def __init__(self, confusion_matrix):
        self.confusion_matrix = confusion_matrix
        self.right = self.get_true_classification()
        self.total = self.get_total_count()

    def get_true_classification(self):
        total = 0
        for key in self.confusion_matrix.keys():
            total += self.confusion_matrix[key][key]
        return total

    def get_total_count(self):
        total = 0
        for key in self.confusion_matrix.keys():
            total += sum(self.confusion_matrix[key].values())
        return total

    def __str__(self):

        str_formatter = ["\t"] + ["    ".join(self.confusion_matrix.keys())]
        str_formatter.append("\n")
        for key in self.confusion_matrix.keys():
            str_formatter.append(key + " " * (3 - len(key)))
            for res in self.confusion_matrix.keys():
                str_formatter.append(str(self.confusion_matrix[key][res]))
                str_formatter.append("    ")
            str_formatter.append("\n")
        str_formatter.append("\nCorrect Classification: %d\n" % self.right)
        str_formatter.append("\nTotal number of images: %d\n" % self.total)
        str_formatter.append("\nAccuracy: %f\n" % round(((float(self.right) / self.total) * 100), 3))

        return ' '.join(str_formatter)


# Read the pixel values and return a list of Pixel objects
def get_pixel_objects(pixels):
    l = len(pixels)
    lst = []
    for i in range(0, l, 3):
        temp = pixels[i:i + 3]
        obj = Pixel(temp[0], temp[1], temp[2])
        lst.append(obj)
    return lst


# Parse a line from the file into ground truth and pixel values.
def process_line(line):
    split_line = line.split()
    key = split_line[0]
    orientation = int(split_line[1])
    pixels = split_line[2:]
    pixel_obj_lst = get_pixel_objects(pixels)

    return key, orientation, pixel_obj_lst


# Returns the training set by reading from the file.
def get_training_set(filename):
    lst = {}
    with open(filename) as f:
        for line in f:
            key, orientation, pixels = process_line(line)
            key_uniq = ''.join([key,'|', str(orientation)])
            lst[key_uniq] = (pixels, int(orientation))
    return lst


# Builds an initial neural network based on the parameters supplied
def build_network(image_pixel_count, hidden_node_count, orientation_count):
    return Network(image_pixel_count, hidden_node_count, orientation_count)


# Returns the expected ground truth as a list of 1s and 0s
def get_orientation_list(orient):
    lst = []
    for x in [0, 90, 180, 270]:
        y = 1 if (orient - x) == 0 else 0
        lst.append(y)
    return lst


# Sigmoid function
# def g(x):
#     res = 1 + (e ** -x)
#     return 1.0/res
#
# def g_prime(x):
#     return g(x) * (1 - g(x))


# Smoothing approximation of the relu function (https://en.wikipedia.org/wiki/Rectifier_(neural_networks) ):
# def g(x):
#     res = 1 + (e ** x)
#     return log(res)


# Leaky ReLu
def g(x):
    return x if x > 0 else (0.01 * x)

# The derivative
# def g_prime(x):
#     res = 1 + (e ** -x)
#     return 1.0 / res


# Leaky ReLu's derivative
def g_prime(x):
    return 1 if x > 0 else 0.01


# Helper to iterate over the values
def iter_helper(range_start, range_end, array, index, multiplier):
    count = 0
    for j in range(range_start, range_end):
        count += (array[j][index] * multiplier[j])
    return count


# Helper to iterate over the values
def iter_helper_backward(range_start, range_end, array, index, multiplier):
    count = 0
    for j in range(range_start, range_end):
        count += (array[index][j] * multiplier[j])
    return count


# Performs a soft max of the output of the output nodes
# To avoid overflow, subtract the max value from each element of the list
# Idea from: http://stackoverflow.com/questions/34968722/softmax-function-python
def soft_max(input_arr):
    lst = input_arr[:]
    max_ele = max(lst)

    for i in range(len(lst)):
        ele = lst[i]
        lst[i] = ele - max_ele
    sum_val = 0

    for i in range(len(lst)):
        lst[i] = e ** lst[i]
        sum_val += lst[i]

    for i in range(len(lst)):
        lst[i] /= sum_val

    return lst


# Forward Propagation
def propagate_forward(network, x, ground_truth):
    propagator = Propagator(ground_truth)
    a = propagator.a
    in_vec = propagator.in_vec

    for i in range(network.input_node_count):
        a[i] = x[i].intensity
        in_vec[i] = x[i].intensity

    for j in range(network.input_node_count, network.hidden_end):
        in_vec[j] = iter_helper(0, network.input_node_count, network.weights, j, a)
        a[j] = g(in_vec[j])

    out_node_vals = []
    for j in range(network.hidden_end, network.output_end):
        in_vec[j] = iter_helper(network.input_node_count, network.hidden_end, network.weights, j, a)
        a[j] = g(in_vec[j])
        out_node_vals.append(a[j])

    soft_max_vals = soft_max(out_node_vals)
    propagator.soft_max_vals = soft_max_vals[:]

    return propagator


# Backward propagation
def propagate_backward(network, propagator):
    for j in range(network.hidden_end, network.output_end):
        propagator.delta[j] = g_prime(propagator.in_vec[j]) * (
            propagator.y[j - network.hidden_end] - propagator.soft_max_vals[j - network.hidden_end])

    for i in range(network.input_node_count, network.hidden_end):
        propagator.delta[i] = g_prime(propagator.in_vec[i])
        propagator.delta[i] *= iter_helper_backward(network.hidden_end, network.output_end, network.weights, i,
                                                    propagator.delta)

    for i in range(network.input_node_count):
        propagator.delta[i] = g_prime(propagator.in_vec[i])
        propagator.delta[i] *= iter_helper_backward(network.input_node_count, network.hidden_end, network.weights, i,
                                                    propagator.delta)
    # Update weights
    for i in network.weights.keys():
        for j in network.weights[i].keys():
            network.weights[i][j] += alpha * propagator.a[i] * propagator.delta[j]

    return network, propagator


# Start learning the values in examples
def learn(examples, network):
    global alpha
    alpha = 1.0 / len(examples)
    print("Learning rate: %f" % alpha)

    local_minima_count = 0
    iteration = 0
    sample_size = 200
    iteration_count = len(examples) / sample_size
    satisfactory_prediction_count = 0.85 * sample_size

    while local_minima_count < 1:  # and iteration < 2000:
        iteration += 1
        right_predictions = 0
        sample_values = sample(examples.values(), sample_size)
        for example in sample_values:
            x = example[0]
            propagator = propagate_forward(network, x, int(example[1]))
            soft_max_vals = propagator.soft_max_vals
            predicted_orientation = get_orientation_value(soft_max_vals.index(max(soft_max_vals)))
            if int(example[1]) == predicted_orientation:
                right_predictions += 1

            network, propagator = propagate_backward(network, propagator)

            del propagator

        print("Learning - %d/%d" % (right_predictions, sample_size))

        if right_predictions >= satisfactory_prediction_count:
            print("Hitting Local minima.")
            local_minima_count += 1
            iteration = 1

        if iteration >= iteration_count:
            satisfactory_prediction_count -= 0.01 * sample_size

            print("Expectations are now %d" % satisfactory_prediction_count)
            iteration = 1

    return network


# Serialize the model
def serialize_network(neural_network, param):
    f_ptr = open(param, "w")
    pickle.dump(neural_network, f_ptr)
    f_ptr.close()


# De-serialize the model from file
def deserialize_network(filename):
    f_ptr = open(filename, 'r')
    obj = pickle.load(f_ptr)
    f_ptr.close()
    return obj


def get_orientation_value(index):
    return orient[index]


# Now test the neural network based on the input supplied.
def test(network, inputs):
    confusion_matrix = defaultdict(Counter)
    pred_lst = []

    # for example in inputs.values():
    for key in inputs.keys():
        example = inputs[key]
        image_file = key.split('|')[0]
        true_orientation = example[1]
        x = example[0]

        propagator = propagate_forward(network, x, true_orientation)

        soft_max_vals = propagator.soft_max_vals
        predicted_orientation = get_orientation_value(soft_max_vals.index(max(soft_max_vals)))
        confusion_matrix[str(true_orientation)][str(predicted_orientation)] += 1
        pred = image_file+' '+str(predicted_orientation)
        pred_lst.append(pred)

    writeFile(pred_lst,'nnet_output.txt')

    result = Result(confusion_matrix)
    return result


# Loads the data, trains the neural network and tests it based on the values in the test file.
def neural_net(train_file, test_file, hidden_node_count, cache_file=False):
    print("Technique being used: Neural net.")
    image_pixel_count = 64
    orientation_count = 4
    if hidden_node_count == 0:
        print("Error in input")
        return False

    if cache_file and os.path.isfile(cache_file):
        neural_network = deserialize_network(cache_file)
        print("Loaded the neural net from file  . That was easy.")
    else:
        examples = get_training_set(train_file)
        print("Training set loaded.")
        network = build_network(image_pixel_count, hidden_node_count, orientation_count)
        print("Initial Network built.")
        neural_network = learn(examples, network)
        if cache_file:
            serialize_network(neural_network, cache_file)

    print(neural_network)
    print("Training complete")
    examples = get_training_set(test_file)
    print("Loaded Test files...")

    res = test(neural_network, examples)

    print(res)