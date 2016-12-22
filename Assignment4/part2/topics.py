from sys import argv
import pickle
from os import linesep

import train
from utils import Model
import test

"""
(1) Problem Formulation:
    Topic modelling is a multi-class classification problem where documents can be classified from a set of topics.
In this problem, training can be fully-supervised, partially supervised or unsupervised. A fully supervised training creates
a model by storing the set of words and its frequency for each topic and the word counts for each topic which is stored
as a file. For partially supervised or unsupervised, model is created based on the available classified documents or random
if unsupervised. With this model, several passes are made on the unclassified documents and after each iteration, the
model is updated.
    Testing is done by loading the model file, and classification is done by maximizing over the probabilities for the set
of words in the document given a topic. We pick the topic which gives the highest probability for the given set of words
in the document. The classified topic is compared against the ground truth and accuracies
and confusion matrix is formulated.

(2) Program Implementation:
    The program takes 'mode', dataset directory, model file and fraction as the command line arguments and performs
training or testing the model based on the 'mode' specified.

Training:
Using the model-file name to write into, directory location and the fraction, the train_data method iterates over
each document, parses the email to fetch the body, sanitizes the content into a list of words. Using the fraction value
the program decides whether to see the classification of the document or not and based on the probabilistic outcome,
it either classifies all the set of words as a topic or adds it to the list of unclassified documents. The model object
is created using the classified data.
With the model, the unclassified documents are iterated over at several passes (12 hardcoded) and updates the model
by calculating the topic for each document. Once the loop terminates or no more changes are being done to the model,
the model object is returned which is serialized with 'model-file' as the filename.
Along with the model, the top ten words for each topic is stored as "distinctive_words.txt". Please note that this
file is not consistent with windows line endings. Do not use windows notepad to view the file.

Testing:
The program deserializes the model-file name supplied as our 'Model' object. Using this object and the dataset directory
for the test files, the program now calculates the probability of each document as a topic and picks the one which
gives the highest probability. The results are formulated into a confusion matrix and the object of class Result is
returned which can be used to display the results on the console.

(3) Problems, Assumptions/Simplifications and design decisions:
    * If the word is not in our model, the probability is randomized. Hence, we could see different results after
      running each time.
    * If the word is not found in a particular topic in our model, it is assigned with a very low probability.
    * For an unsupervised training, the first pass is completely randomizing the topic associations of the document.
    * Instead of multiplying, log addition is done to handle extremely low values.
    * Only the email body is considered for training/testing and stop words, numbers and punctuations are not considered.
Problems and Observations:
    * For low fraction values, the model converges everything into a single topic. At each iteration, the count of
      the dominating document keeps increasing and results become biased.


(4) Accuracies:

The table below shows the accuracy rates obtained for each fraction value. The model files are also checked in along
with the code files where the results have been tested on. The last two digits of the model filename denotes the fraction
supplied while training.

Please note that the accuracies might vary a little during testing as there is a bit of randomness involved for new
words. The confusion matrix will be displayed at the end of testing.

fraction    accuracy
1	        75.1
0.9	        74.1
0.8	        72.93
0.7	        69.80
0.6	        67.89
0.5	        67.91
0.4	        58.31
0.3	        58.13
0.2	        59.69
0.1	        31.38
0	        05.36

"""


# Serializes the model object into a file using pickle
def serialize_model(obj, filename):
    try:
        print("Serializing the model to %s" % filename)
        f_ptr = open(filename, "wb")
        pickle.dump(obj, f_ptr)
        f_ptr.close()
    except pickle.PickleError as p:
        print("Serialization Failed")
        print("Error: %s" % p.message)
        exit(1)
    except Exception as e:
        print("Something went wrong during serialization")
        print("Error: %s" % e.message)
        exit(1)


# De-serializes the file into Model object.
def deserialize_model(model_filename):
    try:
        print("Deserializing from file %s" % model_filename)
        f_ptr = open(model_filename, "rb")
        obj = pickle.load(f_ptr)
        f_ptr.close()
        return obj
    except pickle.PickleError as p:
        print("Deserialization Failed")
        print("Error: %s" % p.message)
        exit(1)
    except Exception as e:
        print("Something went wrong during deserialization")
        print("Error: %s" % e.message)
        exit(1)


if len(argv) < 4:
    print("USAGE: python topics.py mode dataset-directory model-file [fraction]")
    exit(1)

# mode - test/train
mode = argv[1]
# directory where the dataset is present
dataset_dir = argv[2].rstrip("/")
# Name of the model file
model_file = argv[3]
# Fraction of classified data available for training
fraction = None


# Handles writing the top ten words into the file after training
def write_top_words_to_file(obj, filename):
    data = obj.data
    fp = open(filename, "w")
    for topic in data.keys():
        string_formatter = [topic + ":"]
        top_words = data[topic].most_common(10)
        for word in top_words:
            string_formatter.append(word[0])
        line = ' '.join(string_formatter)
        fp.write(line)
        fp.write(linesep)
    fp.close()


if mode == "train":
    if len(argv) != 5:
        print("USAGE: python topics.py mode dataset-directory model-file [fraction]")
        exit(1)
    fraction = float(argv[4])
    print("Training started.")
    print("Please wait as it could take a while to create model...")
    model = train.train_data(dataset_dir, fraction)
    write_top_words_to_file(model, "distinctive_words.txt")
    print("Top 10 words at each topic is written into distinctive_words.txt.")
    serialize_model(model, model_file)
    print("Model File created")
    exit(0)

if mode == "test":
    model = deserialize_model(model_file)
    print("Model loaded successfully.")
    result = test.test_data(model, dataset_dir)
    print(result)
    exit(0)

print("Operation not supported")
exit(1)
